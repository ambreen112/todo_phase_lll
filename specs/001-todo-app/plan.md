# Implementation Plan: In-Memory Python Console Todo App

**Branch**: `001-todo-app` | **Date**: 2025-12-25 | **Spec**: [link to spec.md]
**Input**: Feature specification from `/specs/001-todo-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a command-line Todo application using an agentic architecture pattern as specified. The application will feature a main agent that handles user input/output and command parsing, delegating specific operations to specialized subagents. The system will maintain todos in-memory as dictionaries with id, task, and completion status. The architecture follows the constitution's principles of agentic design and simplicity.

## Technical Context

**Language/Version**: Python 3.13+ (as specified in constitution and spec)
**Primary Dependencies**: None (as specified in constitution for Phase 1)
**Storage**: In-memory Python list/dict (as specified in spec and constitution)
**Testing**: pytest (standard Python testing framework)
**Target Platform**: Cross-platform console application (as specified in spec)
**Project Type**: Single console application (as specified in spec)
**Performance Goals**: Fast response to commands (under 2 seconds startup, near-instant response to commands)
**Constraints**: No external dependencies, in-memory only, console-based interface
**Scale/Scope**: Single user console application supporting basic todo operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **AI-Native Engineering**: All implementation will be AI-generated from specs, no manual code writing
- **Agentic Architecture**: Implementation will follow the specified agent structure with main agent, subagents, and shared skills
- **Simplicity for Phase 1**: In-memory storage only, console-based CLI, no external dependencies
- **Spec-Driven Integrity**: Implementation will follow the detailed specification with testable requirements
- **Python Standards**: Implementation will use Python 3.13+ with clean, readable, error-handled code

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── agents/
│   ├── __init__.py
│   ├── main_agent.py          # Main agent with input loop and command parsing
│   ├── add_update_agent.py    # Add/Update subagent
│   ├── list_search_agent.py   # List/Search subagent
│   └── delete_complete_agent.py  # Delete/Complete subagent
├── skills/
│   ├── __init__.py
│   ├── storage_skill.py       # Storage skill for managing in-memory list
│   ├── id_generator_skill.py  # ID generator skill for auto-incrementing IDs
│   └── formatter_skill.py     # Formatter skill for pretty-printing
├── models/
│   ├── __init__.py
│   └── todo.py               # Todo data model
└── cli/
    ├── __init__.py
    └── todo_app.py           # Main application entry point
```

**Structure Decision**: Single project structure chosen as this is a console application with agentic architecture. The structure separates concerns with agents handling business logic, skills providing shared functionality, models defining data structures, and cli providing the user interface layer.

## Agent Architecture Design

### Main Agent Class
- **MainAgent**: Handles the main input loop, command parsing, and delegation to subagents
  - `run()`: Main loop that displays prompt and processes user input
  - `parse_command(input)`: Parses user commands and arguments
  - `delegate_to_subagent(command, args)`: Routes commands to appropriate subagents

### Subagent Classes
- **AddUpdateAgent**: Handles creating and editing todos
  - `add_task(task_text)`: Creates new todo with auto-generated ID
  - `update_task(todo_id, new_task_text)`: Updates existing todo's text
- **ListSearchAgent**: Handles displaying and querying todos
  - `list_all_todos()`: Returns formatted list of all todos
  - `search_todos(query)`: Returns todos matching search query (future extension)
- **DeleteCompleteAgent**: Handles removal and status changes
  - `delete_todo(todo_id)`: Removes todo from list
  - `complete_todo(todo_id)`: Marks todo as complete

### Skill Classes
- **StorageSkill**: Manages in-memory todo list
  - `add_todo(todo)`: Adds todo to list
  - `get_todo_by_id(todo_id)`: Retrieves todo by ID
  - `update_todo_by_id(todo_id, updated_todo)`: Updates todo
  - `delete_todo_by_id(todo_id)`: Removes todo by ID
  - `get_all_todos()`: Returns all todos
- **IDGeneratorSkill**: Auto-increments IDs
  - `generate_next_id()`: Returns next available ID
- **FormatterSkill**: Pretty-prints todo list
  - `format_todo_list(todos)`: Returns formatted string of todos
  - `format_single_todo(todo)`: Returns formatted string of single todo

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
