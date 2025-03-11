from time import sleep
from config.config_handler import ConfigHandler
from fetcher.twitter_post_fetcher import PostFetcher
from repository.user_repository import UserRepository
from services.user_service import UserService
from logger.logger import setup_logger
import os
import logging

class TwitterPuller:
    """
    Class responsible for pulling tweets from Twitter and processing them.

    Attributes:
        config (Dict[str, Any]): Configuration settings loaded from a file.
        post_fetcher (PostFetcher): Instance of a class responsible for fetching posts.
        user_repository (UserRepository): Instance of a class responsible for user data management.
        output_folder_path (str): Path to the folder where output data will be stored.
        execution_interval (int): Interval in milliseconds between each execution of the pull process.
        logger (logging.Logger): Logger instance for logging messages.
    """

    def __init__(self, config_handler: ConfigHandler, post_fetcher: PostFetcher, user_repository: UserRepository):
        """
        Initialize the TwitterPuller with the given configuration handler, post fetcher, and user repository.

        Args:
            config_handler (ConfigHandler): Instance of a class responsible for loading configuration.
            post_fetcher (PostFetcher): Instance of a class responsible for fetching posts.
            user_repository (UserRepository): Instance of a class responsible for user data management.
        """
        self.config = config_handler.load_config('config.json')
        self.post_fetcher = post_fetcher
        self.user_repository = user_repository
        self.output_folder_path = self.config["output_folder_path"]
        self.execution_interval = self.config["execution_interval_ms"]
        self.logger = setup_logger(self.config["log_file_path"])

        if not self.config.get("use_mongodb"):
            os.makedirs(self.output_folder_path, exist_ok=True)

    def run(self):
        """
        Start the process of pulling tweets and processing them in a loop.
        """
        while True:
            self.pull_posts()
            self.logger.info(f"Sleeping for {self.execution_interval / 1000} seconds...")
            sleep(self.execution_interval / 1000)

    def pull_posts(self):
        """
        Pull tweets for all users and process them.
        """
        users = self.user_repository.load_users()
        user_service = UserService(users, self.post_fetcher, self.config, self.logger)
        user_service.process_users()
        self.user_repository.save_users(users)