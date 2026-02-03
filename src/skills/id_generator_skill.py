"""
ID Generator Skill for auto-incrementing IDs.
"""


class IDGeneratorSkill:
    """
    Generates unique sequential IDs for new todos.
    """

    def __init__(self):
        """
        Initialize the ID generator with starting ID of 0.
        """
        self.current_id = 0

    def generate_next_id(self) -> int:
        """
        Generate the next available ID.

        Returns:
            int: The next sequential ID
        """
        self.current_id += 1
        return self.current_id

    def reset(self) -> None:
        """
        Reset the ID generator back to 0.
        """
        self.current_id = 0