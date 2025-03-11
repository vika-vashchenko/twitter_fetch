"""
Module for processing user data and fetching posts.

Classes:
    UserService: Class responsible for processing user data and fetching posts.
"""

from typing import List, Dict, Any
from models.user import User
from fetcher.twitter_post_fetcher import PostFetcher
import os
import json
from datetime import datetime
from logger.logger import setup_logger
from pymongo import MongoClient

class UserService:
    """
    Class responsible for processing user data and fetching posts.

    Attributes:
        users (List[User]): A list of User instances.
        post_fetcher (PostFetcher): Instance of a class responsible for fetching posts.
        config (Dict[str, Any]): Configuration settings.
        output_folder_path (str): Path to the folder where output data will be stored.
        logger (logging.Logger): Logger instance for logging messages.
        raw_data_collection (Optional[MongoClient.Collection]): MongoDB collection for raw data.
    """

    def __init__(self, users: List[User], post_fetcher: PostFetcher, config: Dict[str, Any], logger: setup_logger):
        """
        Initialize the UserService with the given users, post fetcher, configuration, and logger.

        Args:
            users (List[User]): A list of User instances.
            post_fetcher (PostFetcher): Instance of a class responsible for fetching posts.
            config (Dict[str, Any]): Configuration settings.
            logger (logging.Logger): Logger instance for logging messages.
        """
        self.users = users
        self.post_fetcher = post_fetcher
        self.config = config
        self.output_folder_path = config.get("output_folder_path")
        self.logger = logger

        if self.config.get("use_mongodb"):
            self.mongo_client = MongoClient(self.config.get("mongodb_uri"))
            self.db = self.mongo_client[self.config.get("mongodb_db_name")]
            self.raw_data_collection = self.db["raw_data"]
        else:
            self.raw_data_collection = None

    def process_users(self):
        """
        Process all users by fetching and saving their posts.
        """
        for user in self.users:
            self.process_user(user)

    def process_user(self, user: User):
        """
        Process a single user by fetching and saving their posts.

        Args:
            user (User): The user to process.
        """
        new_posts = self.post_fetcher.fetch_posts(user.user_name, user.since_id)
        if new_posts:
            if self.raw_data_collection is not None:
                existing_data = self.raw_data_collection.find_one({"user_name": user.user_name})
                if existing_data:
                    existing_data["post_list"].extend(new_posts)
                    self.raw_data_collection.update_one(
                        {"user_name": user.user_name},
                        {"$set": {"post_list": existing_data["post_list"], "since_id": new_posts[0]["id"]}}
                    )
                else:
                    self.raw_data_collection.insert_one({
                        "user_name": user.user_name,
                        "since_id": new_posts[0]["id"],
                        "post_list": new_posts
                    })
                self.logger.info(f"Inserted/Updated posts for {user.user_name} in MongoDB")
            else:
                user_folder = os.path.join(self.output_folder_path, user.user_name.strip('@'))
                os.makedirs(user_folder, exist_ok=True)
                output_file = os.path.join(user_folder, f"{user.user_name}.json")
                if os.path.exists(output_file):
                    with open(output_file, 'r') as outfile:
                        existing_data = json.load(outfile)
                    existing_data["post_list"].extend(new_posts)
                    existing_data["since_id"] = new_posts[0]["id"]
                else:
                    existing_data = {
                        "user_name": user.user_name,
                        "since_id": new_posts[0]["id"],
                        "post_list": new_posts
                    }
                with open(output_file, 'w') as outfile:
                    json.dump(existing_data, outfile, indent=4)
                self.logger.info(f"Saved posts for {user.user_name} to file system")

            user.last_refresh = datetime.utcnow().isoformat()
            user.since_id = new_posts[0]["id"]
            self.logger.info(f"Updated last_refresh and since_id for {user.user_name}")
        else:
            self.logger.info(f"No new posts for {user.user_name}")