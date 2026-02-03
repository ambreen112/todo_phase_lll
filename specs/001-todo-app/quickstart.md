# Quickstart Guide: In-Memory Python Console Todo App

## Prerequisites
- Python 3.13+ installed on your system

## Running the Application
1. Navigate to the project directory
2. Execute the main application file: `python todo_app.py`
3. The application will start with the prompt: `Todo> `

## Available Commands
- `add <task description>` - Add a new todo item
- `list` - Display all todo items in a formatted table
- `delete <id>` - Remove a todo item by ID
- `update <id> <new task description>` - Update the text of a todo item
- `complete <id>` - Mark a todo item as complete
- `exit` - Quit the application

## Example Usage
```
Todo> add Buy groceries
Added todo: "Buy groceries" with ID 1
Todo> add Walk the dog
Added todo: "Walk the dog" with ID 2
Todo> list
ID | Task          | Status
1  | Buy groceries | Incomplete
2  | Walk the dog  | Incomplete
Todo> complete 1
Todo 1 marked as complete
Todo> list
ID | Task          | Status
1  | Buy groceries | Complete
2  | Walk the dog  | Incomplete
Todo> exit
Goodbye!
```