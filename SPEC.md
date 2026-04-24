## 1. Project Purpose

Build a **Task Management System** that:

- Starts as an existing command‑line (CLI) Python task app
- Is restructured into clear, separate backend parts
- Is made available through:
  - **FastAPI** (REST endpoints)
  - **FastMCP** (tool‑based interface)
- Uses the **Gemini free tier API** through MCP to handle natural‑language input

Every part of the system must follow the **Canonical System Architecture (Section 3)**.

The system must be built so it can be extended later with:

- New data structures
- New algorithms
- Object‑oriented features
- Design patterns
- Tests and automation

---

## 2. Scope

These rules apply everywhere in the project and must follow the architecture in **Section 3**.

### Constraints

- Data is stored in memory only
- No users or authentication
- No frontend or UI
- No logging framework
- No duplicated logic
- No unnecessary complexity

### Core Rule

All decision‑making logic must live in **one place only**: the service layer.

```text
FastAPI Routes → TaskService ← MCP Tools
````

Nothing else may change task data or make task decisions.

***

## 3. Canonical System Architecture

This section defines the **one correct system design**.\
Nothing elsewhere may conflict with it.

***

### Design Rules

*   All task logic lives in the Service Layer
*   FastAPI and MCP only pass data in and out
*   Only the Service Layer can read or write storage
*   Gemini is required and can be used **only through MCP**
*   Gemini helps interpret requests but never decides outcomes
*   No layer may skip another layer

***

### Overall System Flow



***

### Inside the MCP Layer



*   MCP tools may call Gemini
*   MCP tools must call the service to do anything with tasks

***

### Storage Access



Only the Service Layer is allowed to talk to storage.

***

### Who Can Talk to What

| Layer       | Can use TaskService | Can use Storage | Can use Gemini |
| ----------- | ------------------- | --------------- | -------------- |
| Client      | No                  | No              | No             |
| FastAPI     | Yes                 | No              | No             |
| MCP Tools   | Yes                 | No              | Yes            |
| Gemini API  | No                  | No              | No             |
| TaskService | —                   | Yes             | No             |

***

## 4. Project Structure

The folder layout matches the architecture above.



```text
task-mcp-app/
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── routes/
│   ├── mcp/
│   ├── data/
│   ├── utils/
│   ├── observers/
│   └── tests/
├── docs/
└── scripts/
```

***

## 5. Data Model

Models only **store data**.\
They do not make decisions.



***

## 6. Data Storage (v1)



### Rules

*   Use a list to keep task order
*   Use a map for fast lookup by ID
*   Storage is shared through a singleton
*   Everything is in memory

***

## 7. Service Layer

The Service Layer controls **all task behavior**.

### Required Methods

*   `add_task(title)`
*   `list_tasks()`
*   `delete_task(id)`
*   `mark_complete(id)`
*   `search_tasks(keyword)`
*   `sort_tasks(method="default")`

### Rules

*   Only this layer may change tasks
*   No FastAPI, MCP, or Gemini logic inside
*   Both FastAPI and MCP must reuse it

***

## 8. FastAPI Layer

FastAPI only forwards requests to the service.



It must expose all main task actions.

***

## 9. MCP Layer (Gemini Required)

The MCP layer must include Gemini support.



### Required MCP Tools

*   `add_task`
*   `list_tasks`
*   `delete_task`
*   `mark_complete`
*   `search_tasks`
*   `nl_query_tasks` (uses Gemini)
*   `summarize_tasks` (uses Gemini)

***

## 10. Gemini Integration (Required)

Gemini is required in v1 and must follow these rules:

*   Used only inside MCP
*   Never talks directly to services or storage
*   Provides suggestions only
*   Output must be structured and checked before use



***

## 11. Extensions

All extensions still follow the same architecture.

### Data Structures



### Algorithms



***

## 12. Design Patterns

Patterns are used to organize code, not replace logic.





***

## 13. Testing

Tests should focus on the service layer.



### Minimum

*   Use pytest
*   Test at least:
    *   `add_task`
    *   `list_tasks`

***

## 14. Automation

```bash
uvicorn app.main:app --reload
pytest
```

***

## 15. Rectify Bugs

Some errors must still remain in the service layer:

*   Wrong list usage
*   Broken completion logic
*   Bad search assumptions
*   Confusing variable names

***

## 16. GitHub Issue Phases



***

## 17. Setup Student Deliverables

The setup student must provide:

*   A working FastAPI app
*   A correctly isolated service layer
*   MCP primitives starting structure 
*   Initial tests
*   GitHub issues & Project board
*   Github workflow with Org 
    - Coding Standard
    - Issue PR Templates
*   A complete README
*   Contribution Guidelines

***

## 18. README Requirements

The README must explain:

*   The system architecture
*   How to run FastAPI
*   How to run MCP
*   How to configure Gemini
*   How to run tests
*   Where extensions can be added

***

## 19. Architecture Clarifications

### 19.1 MCP Validation

MCP may only check structure and format.

✅ Allowed:

*   JSON shape checks
*   Allowed action checks

❌ Not allowed:

*   Business logic
*   Task state checks

The service layer handles all meaning and rules.

***

### 19.2 FastAPI and MCP Parity

Both FastAPI and MCP must support:

*   Create
*   List
*   Delete
*   Complete
*   Search

They may look different, but must do the same work internally.

***

### 19.3 Data Structure Rules

Data structures:

✅ May:

*   Manage storage mechanics

❌ Must not:

*   Contain task rules
*   Decide task behavior

All task decisions belong to the Service Layer.

***

## 20. Summary

This specification defines a **clear, strict system design** with:

*   One place for all logic
*   Required Gemini integration
*   Clean separation of responsibilities
*   Strong support for learning and extension

All implementations must follow **Section 3: Canonical System Architecture**.