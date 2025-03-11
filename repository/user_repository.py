"""
Module for managing user data.

Classes:
    UserRepository: Class responsible for user data management.
"""

import json
from typing import List, Dict, Any
from models.user import User
from pymongo import MongoClient
import logging

class UserRepository:
    """
    Class responsible for user data management.

    Attributes:
        file_path (str): The path to the user data file.
        config (Dict[str, Any]): Configuration settings.
        logger (logging.Logger): Logger instance for logging messages.
    """

    def __init__(self, file_path: str, config: Dict[str, Any]):
        """
        Initialize the UserRepository with the given file path and configuration.

        Args:
            file_path (str): The path to the user data file.
            config (Dict[str, Any]): Configuration settings.
        """
        self.file_path = file_path
        self.config = config
        self.logger = logging.getLogger()

        if self.config.get("use_mongodb"):
            self.mongo_client = MongoClient(self.config.get("mongodb_uri"))
            self.db = self.mongo_client[self.config.get("mongodb_db_name")]
            self.channels_collection = self.db["channels"]

    def load_users(self) -> List[User]:
        """
        Load users from the data source.

        Returns:
            List[User]: A list of User instances.
        """
        if self.config.get("use_mongodb"):
            users_data = list(self.channels_collection.find())
            self.logger.info(f"Loaded {len(users_data)} users from MongoDB")
            return [User(user_name=user["user_name"], last_refresh=user["last_refresh"], since_id=user.get("since_id")) for user in users_data]
        else:
            with open(self.file_path, 'r') as file:
                users_data = json.load(file)["users"]
                self.logger.info(f"Loaded {len(users_data)} users from {self.file_path}")
                return [User(user_name=user["user_name"], last_refresh=user["last_refresh"], since_id=user.get("since_id")) for user in users_data]

    def save_users(self, users: List[User]):
        """
        Save users to the data source.

        Args:
            users (List[User]): A list of User instances to save.
        """
        if self.config.get("use_mongodb"):
            for user in users:
                self.channels_collection.update_one(
                    {"user_name": user.user_name},
                    {"$set": {"last_refresh": user.last_refresh, "since_id": user.since_id}},
                    upsert=True
                )
        else:
            with open(self.file_path, 'w') as file:
                json.dump({"users": [user.__dict__ for user in users]}, file, indent=4)
            self.logger.info(f"Saved {len(users)} users to {self.file_path}")

    def load_users_from_json(self):
        """
        Load users from a JSON file and insert them into MongoDB.

        Raises:
            Exception: If an error occurs while loading users from the JSON file.
        """
        try:
            with open(self.file_path, 'r') as file:
                users_data = json.load(file)["users"]
                for user in users_data:
                    if not self.channels_collection.find_one({"user_name": user["user_name"]}):
                        self.channels_collection.insert_one(user)
                        self.logger.info(f"Inserted {user['user_name']} into MongoDB")
        except Exception as e:
            self.logger.error(f"Failed to load users from JSON file: {e}")