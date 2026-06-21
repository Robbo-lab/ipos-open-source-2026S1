# MCP Tools Naming Guide

## Purpose 

This document defines the naming convention used for MCP tools
with the project. The goal is to ensure that tool names are predicatable,
human-readable, and consistent across implementation, tests and documentation.

## Naming convention:

All MCP tool names MUST follow this structure:
> `<action>_<target>`

### 1. Action (what the tool does)
The action describes the operation being performed.

Common actions include:
- convert → unit or format conversion
- calculate → mathematical computation
- create → create a resource
- delete → remove a resource
- get → retrieve a resource
- update → modify a resource

Additional actions may be added only when necessary,
but reuse of existing actions is preferred.

### 2. Target (what the tool operates on)
The target describes the domain or object being acted upon.
Examples:
- miles_to_km
- task

Targets should be:
- lowercase or snake_case
- descriptive
- consistent across related tools

### Additional context
Examples of tool names

| Intended Behaviour          | MCP Tool Name         |
| --------------------------- | --------------------- |
| Convert miles to kilometers | `convert_miles_to_km` |
| Convert km to miles         | `convert_km_to_miles` |
| Calculate distance          | `calculate_distance`  |
| Get task by id              | `get_task_by_id`      |
| Delete task by name         | `delete_task_by_name` |
| Filter tasks by type        | `filter_task_by_type` |

### Design Rules
- Tool names MUST NOT be auto-generated route names
- Tool names MUST be stable and human-readable
- Tool names MUST match:
  - implementation
  - tests
  - documentation (README / guides)