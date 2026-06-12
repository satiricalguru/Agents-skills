---
name: mongodb
description: >-
  Use this skill when the user wants to connect to, configure, query, schema-design,
  index, troubleshoot, or scale MongoDB databases. Covers Native Driver and Mongoose
  patterns, transaction sessions, performance explain plans, and serverless database
  connection caching.
compatibility: Applicable to self-hosted, Docker, and MongoDB Atlas deployments.
---

# MongoDB Database Operations and Engineering

MongoDB is a document-oriented NoSQL database. When integrating or writing queries for MongoDB, developers must balance document structure, indexing rules, and aggregation logic to achieve peak performance and maintainable code.

## 1. Setup & Connection Patterns

Always secure MongoDB credentials via environment variables. Use the standard URI structure:
`mongodb://<username>:<password>@<host>:<port>/<database>` or SRV format: `mongodb+srv://...`

### A. Native MongoDB Driver (Node.js)
Initialize a shared client connection block to avoid creating multiple clients:
```typescript
import { MongoClient, Db } from 'mongodb';

const uri = process.env.MONGODB_URI!;
let client: MongoClient;
let db: Db;

export async function connectToDatabase(dbName: string): Promise<Db> {
  if (db) return db;
  
  client = new MongoClient(uri, {
    maxPoolSize: 10,
    minPoolSize: 2,
    connectTimeoutMS: 5000,
  });
  
  await client.connect();
  db = client.db(dbName);
  console.log('Successfully connected to MongoDB');
  return db;
}
```

### B. Mongoose ODM (Node.js)
```typescript
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

export async function dbConnect() {
  if (mongoose.connection.readyState >= 1) return;

  try {
    await mongoose.connect(MONGODB_URI, {
      autoIndex: process.env.NODE_ENV !== 'production', // Disable auto-indexing in production
    });
    console.log('Connected to Mongoose');
  } catch (error) {
    console.error('Mongoose connection error:', error);
    throw error;
  }
}
```

### C. Serverless Connection Caching (Next.js / AWS Lambda)
In serverless environments, database connections will exhaust socket resources if re-opened on every invocation. Cache the connection promise:
```typescript
import mongoose from 'mongoose';

let cached = (global as any).mongoose;

if (!cached) {
  cached = (global as any).mongoose = { conn: null, promise: null };
}

export async function dbConnect() {
  if (cached.conn) return cached.conn;

  if (!cached.promise) {
    cached.promise = mongoose.connect(process.env.MONGODB_URI!).then((m) => m);
  }
  
  try {
    cached.conn = await cached.promise;
  } catch (e) {
    cached.promise = null;
    throw e;
  }

  return cached.conn;
}
```

---

## 2. Data Modeling & Mongoose Schemas

Define models carefully. In MongoDB, consider whether to **Embed** (denormalize) or **Reference** (normalize) related documents:
*   **Embed**: For 1-to-1 or bounded 1-to-many relationships (e.g., user addresses, order line items).
*   **Reference**: For unbounded 1-to-many or many-to-many relationships (e.g., users to comments, books to authors).

### A. Mongoose Schema Definition
```typescript
import { Schema, model, Document } from 'mongoose';

export interface IUser extends Document {
  email: string;
  name: string;
  role: 'user' | 'admin';
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema = new Schema<IUser>({
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\S+@\S+\.\S+$/, 'Please provide a valid email'],
  },
  name: {
    type: String,
    required: true,
    trim: true,
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user',
  },
  metadata: Schema.Types.Mixed,
}, {
  timestamps: true, // Auto-manages createdAt and updatedAt
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Compound Index to prevent duplicate index names on scoped keys
UserSchema.index({ role: 1, email: 1 });

export const User = model<IUser>('User', UserSchema);
```

### B. Pre and Post Middleware (Hooks)
```typescript
// Hash passwords pre-save
UserSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  // Perform hashing logic
  next();
});
```

---

## 3. CRUD Queries & Operator Syntax

Use the correct update and filter operators. Avoid overwriting complete documents on updates.

### A. Update Operators
*   `$set`: Overwrites specific fields only.
*   `$unset`: Deletes fields from a document.
*   `$inc`: Increments field value (positive/negative numeric).
*   `$push`: Appends an element to an array.
*   `$pull`: Removes elements from an array matching a criteria.
*   `$addToSet`: Adds element to array only if it does not already exist.

```typescript
// Update user metadata, increment sign-in count, add a tag
const updatedUser = await User.findOneAndUpdate(
  { email: 'user@example.com' },
  { 
    $set: { 'metadata.lastSeen': new Date() },
    $inc: { loginCount: 1 },
    $addToSet: { tags: 'active' }
  },
  { new: true, runValidators: true } // Return updated doc & run validations
);
```

### B. Array & Subdocument Querying
To query elements within an array of objects, use `$elemMatch`:
```typescript
// Find users having an address in California
const usersInCA = await User.find({
  addresses: {
    $elemMatch: { state: 'CA', active: true }
  }
});
```

---

## 4. Advanced Aggregation Framework

For complex data transformations, reporting, and joins, use MongoDB Aggregation pipelines.

```typescript
const report = await Order.aggregate([
  // Stage 1: Filter orders completed in the last 30 days
  {
    $match: {
      status: 'completed',
      createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
    }
  },
  // Stage 2: Join with customer details
  {
    $lookup: {
      from: 'users', // Name of target collection
      localField: 'userId',
      foreignField: '_id',
      as: 'customer'
    }
  },
  // Stage 3: Unwind client array to object
  {
    $unwind: '$customer'
  },
  // Stage 4: Group by customer and compute statistics
  {
    $group: {
      _id: '$customer._id',
      customerName: { $first: '$customer.name' },
      totalSpent: { $sum: '$totalAmount' },
      orderCount: { $sum: 1 },
      averageOrderValue: { $avg: '$totalAmount' }
    }
  },
  // Stage 5: Sort by spending hierarchy
  {
    $sort: { totalSpent: -1 }
  },
  // Stage 6: Limit output
  {
    $limit: 10
  }
]);
```

---

## 5. Performance, Indexing & Troubleshooting

Slow queries occur when database searches perform a Collection Scan (`COLLSCAN`) instead of an Index Scan (`IXSCAN`).

### A. Explain Plans
Use the `.explain()` method to diagnose slow queries:
```typescript
const explanation = await User.find({ role: 'admin' }).explain('executionStats');
console.log(explanation.executionStats);
```
Look for:
*   `totalDocsExamined`: Should be as close as possible to the number of returned documents. If it matches the total collection size, no index was used.
*   `stage`: `IXSCAN` is desired. `COLLSCAN` indicates a table scan.

### B. Indexing Strategies
Follow the **ESR Rule** for Compound Indexes:
1.  **Equality**: Fields queried with exact matches first (e.g., `status: 'active'`).
2.  **Sort**: Fields used for sorting second (e.g., `createdAt: -1`).
3.  **Range**: Fields queried with inequalities last (e.g., `age: { $gte: 21 }`).

Example index matching `find({ status: 'active', age: { $gte: 21 } }).sort({ name: 1 })`:
```typescript
schema.index({ status: 1, name: 1, age: 1 });
```

---

## 6. Multi-Document Transactions

Transactions guarantee ACID properties across multiple documents. Note: Transactions require MongoDB Replica Sets or Sharded Clusters.

```typescript
import mongoose from 'mongoose';

async function processOrder(userId: string, orderData: any) {
  const session = await mongoose.startSession();
  session.startTransaction();
  
  try {
    // 1. Create order
    const [order] = await Order.create([orderData], { session });
    
    // 2. Deduct inventory balance
    const updatedInventory = await Inventory.findOneAndUpdate(
      { itemId: orderData.itemId, stock: { $gte: orderData.quantity } },
      { $inc: { stock: -orderData.quantity } },
      { session, new: true }
    );
    
    if (!updatedInventory) {
      throw new Error('Insufficient inventory stock');
    }
    
    // 3. Update customer loyalty points
    await User.findByIdAndUpdate(
      userId,
      { $inc: { loyaltyPoints: Math.floor(orderData.totalAmount) } },
      { session }
    );
    
    // Commit transaction
    await session.commitTransaction();
    return order;
  } catch (error) {
    // Abort transaction and roll back all changes
    await session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
}
```

---

## 7. Atlas Search & Vector Embeddings

MongoDB Atlas integrates Lucene-based search directly on collections.

### A. Atlas Search Stage ($search)
Use Atlas Search instead of regex filters for complex, full-text fuzzy matching:
```typescript
const results = await Product.aggregate([
  {
    $search: {
      index: 'default_search_index',
      text: {
        query: 'wireless headphones',
        path: ['title', 'description'],
        fuzzy: { maxEdits: 1 }
      }
    }
  },
  { $limit: 5 }
]);
```

### B. Vector Search ($vectorSearch)
Atlas supports semantic search queries using AI embeddings:
```typescript
const matches = await Product.aggregate([
  {
    $vectorSearch: {
      index: 'vector_index',
      path: 'embedding',
      queryVector: [0.012, -0.45, 0.99, ...],
      numCandidates: 100,
      limit: 5
    }
  }
]);
```
Format of the Atlas vector index definition:
```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```
