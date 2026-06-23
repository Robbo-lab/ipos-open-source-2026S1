# Overall Project Code Review

## 1. Current project state

The repository currently contains three overlapping directions:

- a running FastAPI + FastMCP unit-converter application exposed from `main.py`
- a separate task CRUD path backed by SQLite in `app/api/task_handler.py`, `app/routes/route_tasks.py`, and `app/services/database.py`
- a provider-agnostic Gemini client layer in `app/llm/providers/gemini/client.py`

The startup path, README, MCP tools, prompts, resources, and most tests are still converter-oriented, while the task implementation is partial and not wired into MCP.

## 2. Specification alignment summary

Status: **not aligned**

Why:

- the live app bootstraps a converter server, not the required task system
- task logic is not isolated in a transport-neutral service layer
- storage is persistent SQLite, not in-memory list/map storage
- MCP does not provide the required task tools
- Gemini exists, but not inside a task MCP flow
- documentation describes the wrong system
- default tests do not focus on the task service layer

## 3. Architecture review

### Service layer

- Current state: `app/services/` only contains DB helpers; task behavior lives in `app/api/task_handler.py`.
- Alignment: Not aligned.
- Problems: `TaskHandler` is effectively the service, but it sits in `app/api`, depends directly on `DBTask` and `DataBaseMethods`, and raises `HTTPException` from task logic. Required methods like `search_tasks` and `sort_tasks` do not exist.
- Recommended action: Replace `TaskHandler` with a real `TaskService` under `app/services/`, make it transport-neutral, and make storage a dependency behind a small in-memory boundary.

### FastAPI layer

- Current state: task routes call `TaskHandler` directly and the root/system routes still identify the app as `unit-converter-mcp-server`.
- Alignment: Not aligned.
- Problems: routes are thin in some places, but they still depend on DB sessions and service-like handler code. There is also a correctness bug: `TaskHandler.get_task()` returns `False` on misses, while routes only check `None`, so 404 handling is broken.
- Recommended action: keep routes as request/response adapters only; move decisions and missing-task semantics into the service layer.

### MCP layer

- Current state: MCP is generated from the FastAPI converter app and exposes conversion tools/resources/prompts from `main.py` and `app/mcp/mcp_tools/miles_to_km.py`.
- Alignment: Not aligned.
- Problems: required task MCP tools are absent; current MCP logic is for unit conversion only. MCP is not calling a task service because no task MCP path exists on `main`.
- Recommended action: implement the required task tools on top of `TaskService`, then add Gemini-backed `nl_query_tasks` and `summarize_tasks` there.

### Gemini integration

- Current state: Gemini client code is present and reasonably isolated in `app/llm/providers/gemini/client.py`, plus an example client.
- Alignment: Partially aligned in isolation, not aligned in product flow.
- Problems: Gemini is not connected to task MCP operations at all. The repo is also drifting toward broader multi-provider and HTTP LLM APIs in backlog/PRs, which conflicts with the current spec.
- Recommended action: keep Gemini usage only inside task MCP tools and reject additional provider/API surface area until the approved architecture is implemented.

### Storage/data layer

- Current state: storage uses SQLite at `sqlite:///./Database.db`, SQLAlchemy models live in `app/data/database_objects.py`, and tables are created at import time.
- Alignment: Not aligned.
- Problems: persistent DB storage violates the in-memory-only v1 rule; storage helpers raise `HTTPException`; the repo currently has `Database.db` artifacts in play.
- Recommended action: remove persistence from the task path and replace it with a simple in-memory store owned by the service layer.

## 4. Testing review

- Current tests: LLM and converter validation tests are in much better shape than task tests. Default `pytest` discovery only includes `tests/mcp` and `tests/llm`, so `tests/misc/test_tasks.py` is not part of the default suite.
- Missing tests: default service-layer task tests, FastAPI task-route tests, MCP task-tool tests, Gemini task-flow tests.
- Risk areas: task regressions can land without being exercised by default CI; MCP tests currently depend on a live server and failed locally with `httpx.ConnectError` when none was running.
- Recommended action: revise `#60`, keep `#66` and `#110`, and make task tests self-contained and included in default `pytest`.

## 5. Documentation review

- Current documentation state: heavily stale. `README.md` still documents a converter server; Sphinx only references `task_handler` and `miles_to_km`; curl docs are converter-focused.
- Gaps: no accurate task-architecture guide, no task MCP usage docs, no up-to-date folder/flow explanation, and no clear explanation of current test expectations.
- Recommended action: rewrite README and architecture docs after the service/MCP direction is corrected; do not patch the stale converter wording piecemeal unless it is a small unblocker.

## 6. Open issues review

| Issue | Current intent                                  | Keep / Update / Split / Close later | Reason                                                                       |
| ----- | ----------------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------- |
| #112  | local file storage for MCP primitives           | Close later                         | Out of scope for in-memory v1                                                |
| #111  | remove example client and unused deps           | Keep                                | Reduces complexity                                                           |
| #110  | fix `TestClient` deprecation warning            | Keep                                | Real test hygiene issue                                                      |
| #109  | add reusable curl commands                      | Keep                                | Useful once docs are corrected                                               |
| #108  | extend LLM metrics/cost tracking                | Close later                         | Not part of required v1                                                      |
| #107  | improve MCP resource structure                  | Keep                                | Low-risk internal cleanup                                                    |
| #106  | implement API usage prompt                      | Keep                                | Small MCP-docs improvement                                                   |
| #95   | create task DB object                           | Close later                         | Already partly landed and conflicts with in-memory spec                      |
| #87   | type hints + DB URL from env                    | Update                              | Useful cleanup, but current DB direction is wrong                            |
| #80   | create task app tools                           | Update                              | Should be refocused to service-backed required task MCP tools                |
| #79   | custom HTTP exception class                     | Keep                                | Can support cleaner transport boundaries                                     |
| #78   | replace custom Gemini models with GenAI library | Close later                         | Secondary concern before task architecture exists                            |
| #76   | add LLM provider setup links to README          | Update                              | Should be absorbed into full README rewrite                                  |
| #74   | unified API to call model chat completion       | Close later                         | Conflicts with Gemini-only-through-MCP rule                                  |
| #73   | add Claude/OpenAI/OpenRouter support            | Close later                         | Out of scope vs current spec                                                 |
| #66   | MCP test client factory                         | Keep                                | Helps self-contained tests                                                   |
| #64   | event hook interface                            | Close later                         | Unnecessary infrastructure for v1                                            |
| #63   | shared HTTP/MCP response helper                 | Keep                                | Small boundary cleanup                                                       |
| #62   | extract token decoder                           | Close later                         | Auth is out of scope for v1                                                  |
| #61   | centralise configuration                        | Keep                                | Good cleanup, small scope                                                    |
| #60   | add service-layer tests                         | Update                              | Should target the actual `TaskService` and default pytest run                |
| #59   | add repository boundary over DB layer           | Update                              | Should target in-memory task storage, not DB abstraction                     |
| #55   | shared registry for task handlers               | Close later                         | Premature abstraction                                                        |
| #54   | shared processing contract for MCP task logic   | Update                              | Should become a direct service-calling MCP issue, not handler framework work |
| #53   | shared converter interface                      | Close later                         | Wrong domain for target app                                                  |
| #51   | typed MCP tool definitions                      | Keep                                | Acceptable low-risk cleanup                                                  |
| #50   | typed prompt definitions                        | Keep                                | Acceptable low-risk cleanup                                                  |
| #49   | typed resource structure                        | Keep                                | Acceptable low-risk cleanup                                                  |
| #47   | align miles-to-km validation                    | Keep                                | Valid current bug, low priority to spec                                      |
| #45   | fix README curl path                            | Update                              | Likely superseded by broader docs rewrite                                    |

## 7. Open PR review summary

| PR   | Linked issue                       | Main change                                                             | Risk level | Review priority |
| ---- | ---------------------------------- | ----------------------------------------------------------------------- | ---------- | --------------- |
| #75  | #74                                | adds multi-provider LLM layer, HTTP LLM routes, queueing, spec edits    | Critical   | Highest         |
| #102 | #80                                | adds task MCP tools and permissions on top of current DB/handler design | High       | Highest         |
| #103 | #16                                | adds centralised logging helper/decorator                               | High       | High            |
| #93  | #62 in intent, not formally linked | auth/token refactor with out-of-scope security behavior                 | High       | High            |
| #92  | #87                                | DB URL env + type hints, but broad collateral changes                   | Medium     | Medium          |
| #100 | #61                                | typed settings module                                                   | Medium     | Medium          |
| #83  | #31                                | architecture docs update, but still based on drifting structure         | Medium     | Medium          |
| #99  | #49                                | typed MCP resource definitions                                          | Low        | Low             |
| #81  | #40                                | remove `.DS_Store` and update `.gitignore`                              | Low        | Low             |
| #105 | #44                                | MCP tool naming guide draft                                             | Low        | Low             |

## 8. Missing issue recommendations

### Suggested issue: Revise `#59` into “Replace SQLite task storage with an in-memory TaskService boundary”

**Type:** Architecture  
**Priority:** Critical  
**Problem:** The current task path uses SQLite, SQLAlchemy models, and DB helpers directly from task logic.  
**Why it matters:** This violates the core spec rules for in-memory v1 storage and service-layer ownership.  
**Acceptance criteria:**

- add a transport-neutral `TaskService` under `app/services/`
- replace task persistence with a simple in-memory store owned by the service
- remove `HTTPException` and direct SQLAlchemy dependencies from task behavior

**Suggested implementation notes:** Port current add/get/list/delete/complete behavior first; do not redesign unrelated converter code in the same issue.

### Suggested issue: Revise `#80` into “Implement required task MCP tools and Gemini task flows through TaskService”

**Type:** MCP / Gemini  
**Priority:** Critical  
**Problem:** The live MCP surface is still converter-only, and task tools are not exposed from `main`.  
**Why it matters:** The spec explicitly requires task MCP tools plus Gemini-backed `nl_query_tasks` and `summarize_tasks`.  
**Acceptance criteria:**

- add `add_task`, `list_tasks`, `delete_task`, `mark_complete`, `search_tasks`
- add `nl_query_tasks` and `summarize_tasks` using Gemini only inside MCP
- all task MCP operations call `TaskService`, not storage

**Suggested implementation notes:** Keep Gemini output structured and validated before any service call.

### Suggested issue: Revise `#60` into “Make task service tests the default, self-contained pytest path”

**Type:** Test  
**Priority:** High  
**Problem:** current task tests exist but are outside default `pytest`, while MCP tests depend on an externally running server.  
**Why it matters:** The spec says testing should focus mainly on the service layer.  
**Acceptance criteria:**

- include task service tests in default `pytest`
- add focused FastAPI task-route tests
- make MCP tests run in-process or explicitly bootstrap the server

**Suggested implementation notes:** Keep the first pass small: fix discovery first, then replace live-server assumptions.

### Suggested issue: Rewrite README and architecture docs to match the approved task app

**Type:** Documentation  
**Priority:** High  
**Problem:** the repository documentation still describes a converter server and outdated architecture.  
**Why it matters:** Current docs misdirect contributors and encourage work against the wrong system.  
**Acceptance criteria:**

- README describes the task system, not the converter app
- docs explain the service/FastAPI/MCP/Gemini boundaries accurately
- curl and testing examples match the real task flows

**Suggested implementation notes:** Do this after the service and MCP issues above, not before.

## 9. Recommended issue order

1. Close or rewrite out-of-scope backlog items: `#112`, `#74`, `#73`, `#62`, `#64`, `#55`, `#53`, and likely `#95`.
2. Revise and implement `#59` so the task architecture matches the in-memory service-layer design.
3. Refactor FastAPI task routes to become thin service adapters.
4. Revise and implement `#80` so MCP exposes the required task tools and Gemini task flows.
5. Revise and implement `#60`, then keep `#66` and `#110` to stabilise automated testing.
6. Rewrite docs using the corrected architecture, absorbing `#45` and `#76`.
7. Triage low-risk cleanup items like `#61`, `#63`, `#49`, `#50`, `#51`, and `#107`.

## 10. Approval checkpoint

This review is complete and has been saved as a read-only planning artifact.

Prompt for next step:

`Confirm if you want me to continue in read-only mode only. No issues or code changes will happen unless you explicitly ask for them.`
