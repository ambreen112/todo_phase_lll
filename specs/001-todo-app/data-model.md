# Data Model for In-Memory Python Console Todo App

## Todo Entity
- **id**: integer (unique identifier, auto-incremented)
- **task**: string (the task description text)
- **complete**: boolean (indicates completion status)

## Todo List Collection
- **Structure**: Python list containing Todo entities
- **Operations**:
  - Add new todos to the list
  - Retrieve todos by ID
  - Update todos by ID
  - Delete todos by ID
  - List all todos

## Validation Rules
- **ID uniqueness**: Each Todo must have a unique ID
- **Task non-empty**: When adding or updating, task text should not be empty
- **ID existence**: Operations requiring an ID should validate the ID exists before proceeding

## State Transitions
- **Todo Creation**: New Todo created with `complete = False`
- **Todo Completion**: `complete` changes from `False` to `True`
- **Todo Deletion**: Todo is removed from the collection entirely