# Flow Builder Type Documentation

This document describes the data structure contract between the frontend (TypeScript/React) and backend (Python) for the flow builder system.

## Overview

The flow builder allows users to create conversational flows with various node types. Data is created in the frontend and executed in the backend, so type consistency is critical.

## Flow Data Structure

### Root Structure
```json
{
  "nodes": [...],  // Array of FlowNode
  "edges": [...]   // Array of FlowEdge
}
```

## Node Types

All nodes follow this base structure:
```json
{
  "id": "string",           // Unique identifier (e.g., "start-1", "message-1234567890")
  "type": "string",         // Node type (see below)
  "position": {             // Position on canvas
    "x": number,
    "y": number
  },
  "data": {...}            // Node-specific data (see below)
}
```

### 1. Start Node
**Type:** `"start"`

**Data Structure:**
```typescript
{
  label: string  // Display name (typically "Start")
}
```

**Python Example:**
```python
{
    "id": "start-1",
    "type": "start",
    "position": {"x": 100, "y": 200},
    "data": {"label": "Start"}
}
```

**Purpose:** Entry point of the flow. Must have exactly one per flow.

---

### 2. Message Node
**Type:** `"message"`

**Data Structure:**
```typescript
{
  label: string,   // Display name
  message: string  // The message content to display
}
```

**Python Example:**
```python
{
    "id": "welcome-1",
    "type": "message",
    "position": {"x": 350, "y": 150},
    "data": {
        "label": "Welcome",
        "message": "Welcome to UniverBot!"
    }
}
```

**Purpose:** Displays a static message to the user.

---

### 3. Chat Input Node
**Type:** `"chatInput"`

**Data Structure:**
```typescript
{
  label: string,          // Display name
  variableName: string    // Variable to store user input (default: "user_message")
}
```

**Python Example:**
```python
{
    "id": "chat-1",
    "type": "chatInput",
    "position": {"x": 700, "y": 280},
    "data": {
        "label": "Chat",
        "variableName": "user_message"
    }
}
```

**Purpose:** Captures user input from the chat interface.

---

### 4. AI Response Node
**Type:** `"aiResponse"`

**Data Structure:**
```typescript
{
  label: string,              // Display name
  inputVariable: string,      // Input variable name (default: "user_question")
  useKnowledgeBase: boolean,  // Whether to use RAG/knowledge base
  prompt?: string            // Optional custom system prompt
}
```

**Python Example:**
```python
{
    "id": "ai-1",
    "type": "aiResponse",
    "position": {"x": 1000, "y": 200},
    "data": {
        "label": "Generate AI Answer",
        "inputVariable": "user_question",
        "useKnowledgeBase": True,
        "prompt": "You are a helpful assistant."  # Optional
    }
}
```

**Purpose:** Generates AI response using LLM and optionally RAG with knowledge base.

**Backend Behavior:**
- If `useKnowledgeBase` is `True`: Uses RAG to find relevant context from documents
- If `prompt` is provided: Uses custom prompt, otherwise uses bot's system_prompt
- Checks similarity threshold (0.7) before using context

---

### 5. Condition Node
**Type:** `"condition"`

**Data Structure:**
```typescript
{
  label: string,      // Display name
  variable: string,   // Variable to check (currently unused)
  condition: string   // Condition to evaluate (simple keyword matching)
}
```

**Python Example:**
```python
{
    "id": "cond-1",
    "type": "condition",
    "position": {"x": 800, "y": 300},
    "data": {
        "label": "Condition",
        "variable": "",
        "condition": "pricing"  # If user message contains "pricing"
    }
}
```

**Purpose:** Routes conversation based on condition. Currently supports simple keyword matching.

**Backend Behavior:**
- Checks if `condition` (lowercase) is contained in user message (lowercase)
- If match: Takes first outgoing edge (true path)
- If no match: Takes second outgoing edge if exists (false path)

**Handles:**
- Has 2 source handles: "true" (top 30%) and "false" (bottom 70%)

---

## Edge Structure

```typescript
{
  id: string,              // Unique identifier (e.g., "e1-2")
  source: string,          // Source node ID
  target: string,          // Target node ID
  animated?: boolean,      // Optional animation
  type?: string,          // Optional edge type (e.g., "smoothstep")
  style?: {               // Optional styling
    stroke?: string,
    strokeWidth?: number,
    strokeDasharray?: string
  }
}
```

**Python Example:**
```python
{
    "id": "e1-2",
    "source": "start-1",
    "target": "welcome-1",
    "animated": True,
    "type": "smoothstep",
    "style": {
        "stroke": "#00E5FF",
        "strokeWidth": 2
    }
}
```

---

## Validation Rules

### Backend Validation (Python)
The backend validates flow data using Pydantic schemas:

1. **Must have at least one node**
2. **Must have exactly one start node** (type: "start")
3. **Valid node types:** "start", "message", "chatInput", "aiResponse", "condition"
4. **All edges must reference existing node IDs**

### Frontend Validation (TypeScript)
- Prevents self-loops (node connecting to itself)
- Validates node types match `nodeTypes` registry
- Ensures proper handle connections

---

## Complete Example Flow

```json
{
  "nodes": [
    {
      "id": "start-1",
      "type": "start",
      "position": {"x": 100, "y": 200},
      "data": {"label": "Start"}
    },
    {
      "id": "welcome-1",
      "type": "message",
      "position": {"x": 350, "y": 150},
      "data": {
        "label": "Welcome",
        "message": "Welcome! How can I help you?"
      }
    },
    {
      "id": "chat-1",
      "type": "chatInput",
      "position": {"x": 700, "y": 280},
      "data": {
        "label": "Chat",
        "variableName": "user_message"
      }
    },
    {
      "id": "ai-1",
      "type": "aiResponse",
      "position": {"x": 1000, "y": 200},
      "data": {
        "label": "AI Response",
        "inputVariable": "user_question",
        "useKnowledgeBase": true
      }
    }
  ],
  "edges": [
    {
      "id": "e1-2",
      "source": "start-1",
      "target": "welcome-1",
      "animated": true
    },
    {
      "id": "e2-3",
      "source": "welcome-1",
      "target": "chat-1"
    },
    {
      "id": "e3-4",
      "source": "chat-1",
      "target": "ai-1"
    },
    {
      "id": "e4-3",
      "source": "ai-1",
      "target": "chat-1",
      "style": {"strokeDasharray": "5,5"}
    }
  ]
}
```

---

## Execution Flow

### 1. First Message (Welcome)
- Backend calls `executor.get_welcome_message()`
- Returns message from first message node after start
- Sets `session_state.current_node_id` to chat input node

### 2. User Message
- Backend calls `executor.execute_flow(user_message, session_state)`
- Gets current node from `session_state.current_node_id`
- If at chatInput node: moves to next node (usually aiResponse)
- Executes node logic and returns response
- Updates session_state with next node ID

### 3. Node Execution
Each node type executes differently:
- **start**: Returns welcome label
- **message**: Returns message content
- **chatInput**: Returns empty (just receives input)
- **aiResponse**: Generates AI response with RAG + LLM
- **condition**: Routes to next node based on condition

---

## Migration Guide

### If you need to add a new node type:

**Frontend:**
1. Create new node component in `frontend/src/components/flow-builder/nodes/`
2. Export it in `nodes/index.ts`
3. Add to `NodePanel.tsx` list
4. Define TypeScript interface for node data

**Backend:**
1. Add node type to `Literal` in `models/schemas.py` FlowNode
2. Create data model class in `schemas.py`
3. Add execution logic in `flow_executor.py` `execute_node()`
4. Handle routing in `get_next_node()` if special routing needed

---

## Common Issues & Fixes

### Issue: Flow not executing
**Cause:** Node type mismatch between frontend and backend
**Fix:** Ensure node.type matches exactly (case-sensitive)

### Issue: Condition node not working
**Cause:** Backend expected "conditionNode" but frontend sends "condition"
**Fix:** Backend now accepts both variants

### Issue: AI response ignores custom prompt
**Cause:** Frontend sends `inputVariable` but backend looks for `prompt`
**Fix:** Backend now checks for both fields

### Issue: Flow validation fails
**Cause:** Invalid flow structure or missing start node
**Fix:** Use FlowData Pydantic model for validation

---

## Testing

To test type compatibility:

1. **Frontend:** Check browser console for flow data before save
2. **Backend:** Check logs for parsed flow structure
3. **API:** Test with `/bots/{bot_id}` PATCH with flow_data
4. **Execution:** Test chat with flow via `/chat/{bot_id}/preview`

---

## Future Improvements

- [ ] Add variable system for passing data between nodes
- [ ] Support complex condition expressions (not just keywords)
- [ ] Add more node types (API call, database query, etc.)
- [ ] Add flow versioning and migration system
- [ ] Add visual flow debugger
- [ ] Add flow templates
