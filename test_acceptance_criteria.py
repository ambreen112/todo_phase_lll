"""
Test script to verify the acceptance criteria scenario:
- Run app, add 2 todos, list them, complete one, delete one, exit.
"""

from src.skills.storage_skill import StorageSkill
from src.skills.id_generator_skill import IDGeneratorSkill
from src.skills.formatter_skill import FormatterSkill
from src.agents.add_update_agent import AddUpdateAgent
from src.agents.list_search_agent import ListSearchAgent
from src.agents.delete_complete_agent import DeleteCompleteAgent
from src.agents.main_agent import MainAgent


def test_acceptance_criteria():
    """
    Test the acceptance criteria scenario: add 2 todos, list them, complete one, delete one.
    """
    print("Testing acceptance criteria scenario...")
    print("1. Setting up components...")

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

    print("2. Adding 2 todos...")
    todo1 = add_update_agent.add_task("Buy groceries")
    print(f"   Added: {todo1.task} with ID {todo1.id}")

    todo2 = add_update_agent.add_task("Walk the dog")
    print(f"   Added: {todo2.task} with ID {todo2.id}")

    print("\n3. Listing all todos...")
    todos_list = list_search_agent.list_all_todos()
    print(f"   Todos:\n{todos_list}")

    print(f"\n4. Completing todo with ID {todo1.id}...")
    success = delete_complete_agent.complete_todo(todo1.id)
    if success:
        print(f"   Todo {todo1.id} marked as complete")
    else:
        print(f"   Failed to complete todo {todo1.id}")

    print("\n5. Listing todos after completion...")
    todos_list = list_search_agent.list_all_todos()
    print(f"   Todos:\n{todos_list}")

    print(f"\n6. Deleting todo with ID {todo2.id}...")
    success = delete_complete_agent.delete_todo(todo2.id)
    if success:
        print(f"   Todo {todo2.id} deleted successfully")
    else:
        print(f"   Failed to delete todo {todo2.id}")

    print("\n7. Listing todos after deletion...")
    todos_list = list_search_agent.list_all_todos()
    print(f"   Todos:\n{todos_list}")

    print("\nAcceptance criteria test completed successfully!")


if __name__ == "__main__":
    test_acceptance_criteria()