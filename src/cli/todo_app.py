"""
Main application entry point for the Todo App.
"""

import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.skills.storage_skill import StorageSkill
from src.skills.id_generator_skill import IDGeneratorSkill
from src.skills.formatter_skill import FormatterSkill
from src.agents.add_update_agent import AddUpdateAgent
from src.agents.list_search_agent import ListSearchAgent
from src.agents.delete_complete_agent import DeleteCompleteAgent
from src.agents.main_agent import MainAgent


def main():
    """
    Initialize and run the Todo application.
    """
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

    # Run the application
    main_agent.run()


if __name__ == "__main__":
    main()