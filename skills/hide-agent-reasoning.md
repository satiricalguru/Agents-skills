---
name: hide-agent-reasoning
description: Keeps the agent's internal reasoning, chain-of-thought, or planning narration out of the visible chat response. Use for every reply, especially with Gemini models (3.5 Flash, 3 Flash, 3.1 Pro) which are known to leak raw thinking text ("Let me think...", "Wait, actually...") straight into the response body instead of a separate reasoning channel.
---

# Hide Agent Reasoning From Chat

## Why this exists
Gemini models write their internal monologue as plain text. Unlike Claude, which
wraps reasoning in a structured, strippable `<thinking>` block, Gemini has no
reliable delimiter between "thinking out loud" and the final answer — so on
some turns the raw deliberation gets typed straight into the chat box. Lowering
the thinking effort reduces how often this happens; it doesn't guarantee it
away. This skill is a second line of defense at the instruction level.

## Rule
- The chat reply is for the user-facing answer only: what was done, what
  changed, what's next. Never the step-by-step internal talk-through of how
  you got there.
- If a response starts drifting into "Let me...", "Wait...", "Actually, the
  rule says...", or numbered internal deliberation — stop, and don't send that
  as the reply.

## Where the thinking should go instead
When a task genuinely needs visible extended reasoning (multi-file changes,
debugging, architecture decisions), don't put it in chat:

1. Write scratch reasoning / the plan to `.agents/scratch/<task-slug>.md` in
   the project (create the folder if it doesn't exist).
2. Use Antigravity's own Task List / Walkthrough / Artifact panel for
   anything that should stay visible but separate from the chat reply — plans,
   step lists, progress updates.
3. Only the final result summary and next steps go into the chat message
   itself.

## Self-check before sending any chat message
Scan the draft reply for reasoning leakage before sending it:
- Sentences that talk through a decision rather than state it
  ("I should probably...", "So the answer is...", "Hmm, actually...").
- Numbered internal deliberation that isn't a user-facing instruction list.
- The model narrating its own rule files or instructions out loud
  ("The X.md says...", "Per the rule above...").

If any of that is present, strip it (or move it to the scratch file per
above) and rewrite the message as a direct, final answer.

## Model-specific notes
- **Gemini 3.5 Flash / Gemini 3 Flash**: default thinking effort is medium.
  Where Antigravity exposes a thinking-effort control for the model, set it to
  low for routine edits/questions — this cuts down leakage and cost. Reserve
  medium/high for tasks that truly need deep multi-step reasoning, and still
  treat that reasoning as internal, not a chat draft.
- **Gemini 3.1 Pro / Gemini 3 Pro**: thinking cannot be disabled for these, so
  the redirect rule above is the main safeguard.
- **Claude models**: reasoning already lives in a structured block the client
  strips automatically — this skill is a no-op for them.

## Known limitation
This is a prompt-level mitigation, not a guaranteed fix. The underlying leak
is an open, upstream issue with how Gemini emits plain-text reasoning — if it
still slips through occasionally, that's the known bug, not a sign the skill
isn't working.
