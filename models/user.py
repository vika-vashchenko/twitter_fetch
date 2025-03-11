"""
Module for defining the User model.

Classes:
    User: Class representing a user.
"""

from typing import Optional

class User:
    """
    Class representing a user.

    Attributes:
        user_name (str): The username of the user.
        last_refresh (Optional[str]): The last refresh time of the user's data.
        since_id (Optional[str]): The ID of the last fetched post.
    """

    def __init__(self, user_name: str, last_refresh: Optional[str] = None, since_id: Optional[str] = None):
        """
        Initialize a User instance.

        Args:
            user_name (str): The username of the user.
            last_refresh (Optional[str]): The last refresh time of the user's data.
            since_id (Optional[str]): The ID of the last fetched post.
        """
        self.user_name = user_name
        self.last_refresh = last_refresh
        self.since_id = since_id