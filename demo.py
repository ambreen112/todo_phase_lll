#!/usr/bin/env python3
"""
Demo script to show the todo application functionality
"""

import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.skills.storage_skill import StorageSkill
from src.skills.id_generator_skill import IDGeneratorSkill
from src.skills.formatter_skill import FormatterSkill
from src.agents.add_update_agent import AddUpdateAgent
from src.agents.list_search_agent import ListSearchAgent
from src.agents.delete_complete_agent import DeleteCompleteAgent
from src.agents.main_agent import MainAgent

def demo():
    print("=== Todo App Demo ===")
    print("Setting up the application components...\n")

    # Initialize skills
    storage_skill = StorageSkill()
    id_generator_skill = IDGeneratorSkill()
    formatter_skill = FormatterSkill()

    # Initialize subagents
    add_update_agent = AddUpdateAgent(storage_skill, id_generator_skill)
    list_search_agent = ListSearchAgent(storage_skill, formatter_skill)
    delete_complete_agent = DeleteCompleteAgent(storage_skill)

    # Initialize main agent
    main_agent = MainAgent(
        add_update_agent,
        list_search_agent,
        delete_complete_agent
    )

    print("1. Adding some todos:")
    todo1 = add_update_agent.add_task("Buy groceries")
    print(f"   Added: '{todo1.task}' with ID {todo1.id}")

    todo2 = add_update_agent.add_task("Walk the dog")
    print(f"   Added: '{todo2.task}' with ID {todo2.id}")

    todo3 = add_update_agent.add_task("Finish project")
    print(f"   Added: '{todo3.task}' with ID {todo3.id}")

    print("\n2. Listing all todos:")
    todos_output = list_search_agent.list_all_todos()
    print(f"   {todos_output}")

    print("\n3. Marking todo #2 as complete:")
    success = delete_complete_agent.complete_todo(2)
    if success:
        print("   Todo #2 marked as complete")
    else:
        print("   Failed to complete todo #2")

    print("\n4. Listing todos after completion:")
    todos_output = list_search_agent.list_all_todos()
    print(f"   {todos_output}")

    print("\n5. Updating todo #1:")
    success = add_update_agent.update_task(1, "Buy groceries and cook dinner")
    if success:
        print("   Todo #1 updated successfully")
    else:
        print("   Failed to update todo #1")

    print("\n6. Listing todos after update:")
    todos_output = list_search_agent.list_all_todos()
    print(f"   {todos_output}")

    print("\n7. Deleting todo #3:")
    success = delete_complete_agent.delete_todo(3)
    if success:
        print("   Todo #3 deleted successfully")
    else:
        print("   Failed to delete todo #3")

    print("\n8. Final list of todos:")
    todos_output = list_search_agent.list_all_todos()
    print(f"   {todos_output}")

    print("\n=== Demo completed ===")

if __name__ == "__main__":
    demo()