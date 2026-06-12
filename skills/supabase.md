---
name: supabase
description: >-
  Use this skill whenever the user wants to integrate, configure, manage, query,
  or troubleshoot Supabase (including PostgreSQL, Authentication, Realtime,
  Edge Functions, Storage, Vector databases, and TypeScript type generation).
  Provides structured guidelines for Row-Level Security (RLS) policies, database
  migrations, and SSR cookie-based auth integration.
compatibility: Best used when Supabase CLI and client libraries are available.
---

# Supabase Development and Integration

Supabase is an open-source Firebase alternative built on top of PostgreSQL. When working on projects utilizing Supabase, you must follow strict guidelines for security (Row-Level Security), type-safety (TypeScript code-gen), and performant database architectures.

## 1. Environment & CLI Setup

Before running operations, determine if the Supabase CLI is installed and check the project status:

```bash
# Check CLI installation
supabase --version

# Initialize a new project in the workspace
supabase init

# Start local Supabase development environment (requires Docker)
supabase start

# Check local development status & get API keys/URLs
supabase status

# Link local repository to a hosted Supabase project
supabase link --project-ref <project-reference-id>
```

---

## 2. Database Migrations & Type Safety

Never perform manual schema changes in the Supabase Dashboard for production environments. Always use code-controlled migration workflows.

### A. Creating & Applying Migrations

1.  **Generate a new migration file**:
    ```bash
    supabase migration new <migration_name>
    ```
    This creates a new SQL file under `supabase/migrations/` prefixed with a timestamp.

2.  **Write SQL schemas**:
    Use clean PostgreSQL DDL syntax. Define foreign keys, check constraints, indexes, and automatic timestamp updates:
    ```sql
    -- Example migration: Creating a profiles table linked to auth.users
    create table public.profiles (
      id uuid references auth.users on delete cascade primary key,
      username text unique not null,
      full_name text,
      avatar_url text,
      updated_at timestamp with time zone default timezone('utc'::text, now()) not null
    );
    ```

3.  **Apply migrations locally**:
    ```bash
    supabase db reset
    ```

4.  **Deploy migrations to the remote database**:
    ```bash
    supabase db push
    ```

### B. TypeScript Schema Type Generation

Always generate type definitions after modifying schemas to maintain strict type safety.

```bash
# Generate types from local database container
supabase gen types typescript --local > types/supabase.ts

# Generate types from remote project
supabase gen types typescript --project-id "<project-reference-id>" > types/supabase.ts
```

Integrate these types when initializing your client:
```typescript
import { createClient } from '@supabase/supabase-js';
import { Database } from '../types/supabase';

export const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);
```

---

## 3. Row-Level Security (RLS) & Policies

**CRITICAL RULE**: Every table created in public schemas MUST have Row-Level Security enabled. Storing data without RLS is a severe security vulnerability.

### A. Enabling RLS
```sql
alter table public.profiles enable row level security;
```

### B. Defining Policies
Write distinct policies for `SELECT`, `INSERT`, `UPDATE`, and `DELETE` actions rather than using `ALL`.

*   **Public Read Access**:
    ```sql
    create policy "Allow public read access"
      on public.profiles for select
      using (true);
    ```

*   **Owner-Only Write Access** (checks if the record ID matches the authenticated user ID):
    ```sql
    create policy "Allow users to update their own profile"
      on public.profiles for update
      to authenticated
      using (auth.uid() = id)
      with check (auth.uid() = id);
    ```

*   **Authenticated Insert Access**:
    ```sql
    create policy "Allow authenticated users to insert a profile"
      on public.profiles for insert
      to authenticated
      with check (auth.uid() = id);
    ```

### C. Policies referencing other tables (Subqueries & Security Definers)
To check permissions against another table, use a subquery or a security-definer helper function to avoid recursive policy resolution:
```sql
create policy "Allow admins to delete profiles"
  on public.profiles for delete
  to authenticated
  using (
    exists (
      select 1 from public.user_roles
      where user_roles.user_id = auth.uid() and user_roles.role = 'admin'
    )
  );
```

---

## 4. Supabase Auth & Session Management

Supabase uses JWTs for authentication. Choose the correct client instantiation pattern depending on your execution environment.

### A. Client-Side (SPA) Auth
```typescript
// Register user
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'securePassword123',
});

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securePassword123',
});

// Listen to auth state transitions
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') console.log('User signed in:', session?.user);
  if (event === 'SIGNED_OUT') console.log('User signed out');
});
```

### B. Server-Side Rendering (SSR) Auth (e.g., Next.js App Router)
Always use `@supabase/ssr` to configure dynamic cookie management. This ensures credentials are authenticated server-side before rendering.

1.  **Middleware Cookie Sync**:
    ```typescript
    import { createServerClient } from '@supabase/ssr';
    import { NextResponse, type NextRequest } from 'next/server';

    export async function updateSession(request: NextRequest) {
      let response = NextResponse.next({ request });

      const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
          cookies: {
            getAll() {
              return request.cookies.getAll();
            },
            setAll(cookiesToSet) {
              cookiesToSet.forEach(({ name, value, options }) => request.cookies.set({ name, value, ...options }));
              response = NextResponse.next({ request });
              cookiesToSet.forEach(({ name, value, options }) => response.cookies.set({ name, value, ...options }));
            },
          },
        }
      );

      await supabase.auth.getUser(); // Refreshes session token if expired
      return response;
    }
    ```

2.  **Server Components**:
    ```typescript
    import { createServerClient } from '@supabase/ssr';
    import { cookies } from 'next/headers';

    export default async function Page() {
      const cookieStore = cookies();
      const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
          cookies: {
            getAll() { return cookieStore.getAll(); },
            // Read-only context, setAll omitted
          },
        }
      );

      const { data: { user } } = await supabase.auth.getUser();
      const { data: posts } = await supabase.from('posts').select('*');
      
      return <div>Hello {user?.email}</div>;
    }
    ```

---

## 5. Advanced Querying & Performance

Write structured queries, handling relationships and pagination efficiently.

### A. Complex Joins & Filtering
Fetch nested records directly using PostgreSQL foreign key relationships:
```typescript
const { data, error } = await supabase
  .from('posts')
  .select(`
    id,
    title,
    content,
    profiles (
      username,
      avatar_url
    ),
    comments (
      id,
      body,
      user_id
    )
  `)
  .eq('status', 'published')
  .order('created_at', { ascending: false })
  .range(0, 9); // Page 1 (10 items)
```

### B. Error Handling & Guard Pattern
Always validate errors returned from queries. Never assume the returned payload is present.
```typescript
const { data, error } = await supabase.from('items').select('*');
if (error) {
  console.error('Database query failed:', error.message, error.details);
  throw new Error(`Failed to fetch items: ${error.hint}`);
}
return data;
```

---

## 6. Realtime Subscriptions

Listen to real-time events on database changes. Ensure the database tables have real-time enabled first.

### A. Enable Realtime on a Table (SQL)
```sql
alter publication supabase_realtime add table public.messages;
```

### B. Subscribe Client (JS/TS)
```typescript
const channel = supabase
  .channel('realtime_messages')
  .on(
    'postgres_changes',
    {
      event: '*', // Listen to INSERT, UPDATE, and DELETE
      schema: 'public',
      table: 'messages',
      filter: 'room_id=eq.lobby' // Optional filtering
    },
    (payload) => {
      console.log('Realtime change received:', payload);
    }
  )
  .subscribe((status) => {
    if (status === 'SUBSCRIBED') console.log('Connected to realtime channel');
  });

// Cleanup subscription on unmount
// channel.unsubscribe();
```

---

## 7. Storage Management

Manage media files, assets, and document directories securely.

### A. Buckets & RLS
Configure storage access control by defining policies on the `storage.objects` table.
```sql
-- Allow authenticated users to upload to public bucket 'avatars'
create policy "Allow authenticated uploads"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'avatars' and auth.uid()::text = (storage.foldername(name))[1]);
```

### B. Uploading and Retrieving Files (JS/TS)
```typescript
// Upload file
const { data, error } = await supabase.storage
  .from('avatars')
  .upload('user-123/avatar.png', fileObject, {
    cacheControl: '3600',
    upsert: true
  });

// Get Public URL
const { data: urlData } = supabase.storage
  .from('avatars')
  .getPublicUrl('user-123/avatar.png');

console.log(urlData.publicUrl);
```

---

## 8. Supabase Edge Functions (Deno)

Build lightweight serverless functions using Deno.

### A. Create Edge Function
```bash
supabase functions new hello-world
```

### B. Advanced Function Handler (Deno TypeScript)
Write correct CORS headers and handle requests gracefully:
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.8"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    const { data: { user }, error: authError } = await supabaseClient.auth.getUser()
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const { name } = await req.json()
    return new Response(JSON.stringify({ message: `Hello ${name}!`, userId: user.id }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
```

### C. Deploy Function
```bash
supabase functions deploy hello-world --project-ref <project-reference-id>
```

---

## 9. Vector Database & Semantic Search (pgvector)

Set up database embeddings for AI features.

### A. Initialize pgvector Extension (SQL)
```sql
-- Enable vector extension
create extension vector;

-- Create table with vector column (e.g., 1536 dimensions for OpenAI embeddings)
create table public.documents (
  id bigint primary key generated always as identity,
  content text not null,
  embedding vector(1536)
);
```

### B. Similarity Search Function (Cosine Similarity)
Create a Postgres function to search matching embeddings:
```sql
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  similarity float
)
language sql stable
as $$
  select
    documents.id,
    documents.content,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by documents.embedding <=> query_embedding
  limit match_count;
$$;
```

### C. Execute RPC via Client
```typescript
const { data, error } = await supabase.rpc('match_documents', {
  query_embedding: [0.1, -0.2, 0.35, ...], // Array of numbers
  match_threshold: 0.78,
  match_count: 5,
});
```
