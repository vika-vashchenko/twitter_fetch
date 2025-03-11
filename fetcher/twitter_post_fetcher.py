import tweepy
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv
import time
import logging

load_dotenv()

BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')


class PostFetcher(ABC):
    """Abstract class for fetching posts from a social media platform"""

    @abstractmethod
    def fetch_posts(self, user_name: str, since_id: str = None) -> List[Dict[str, Any]]:
        """
        Fetch posts for a given user, optionally since a given ID.

        Args:
            user_name (str): The username of the user to fetch posts for.
            since_id (str, optional): The ID of the post to fetch posts since. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the fetched posts.
        """
        pass


class TwitterPostFetcher(PostFetcher):
    """Class for fetching posts from Twitter"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TwitterPostFetcher with the given configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing settings for the fetcher.
        """
        self.client = tweepy.Client(bearer_token=BEARER_TOKEN)
        self.logger = logging.getLogger()
        self.max_results = config.get('max_results', 100)

    def fetch_posts(self, user_name: str, since_id: str = None) -> List[Dict[str, Any]]:
        """
        Fetch posts for a given user from Twitter, optionally since a given ID.

        Args:
            user_name (str): The username of the user to fetch posts for.
            since_id (str, optional): The ID of the post to fetch posts since. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the fetched posts.
        """
        user = self.client.get_user(username=user_name)
        user_id = user.data.id

        query_params = {
            'tweet.fields': 'created_at,public_metrics,entities',
            'exclude': 'retweets,replies',
            'max_results': self.max_results
        }
        if since_id:
            query_params['since_id'] = since_id

        return self._get_tweets_with_retries(user_id, query_params)

    def _get_tweets_with_retries(self, user_id: str, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get tweets for a user with retries in case of rate limit exceeded.

        Args:
            user_id (str): The ID of the user to fetch tweets for.
            query_params (Dict[str, Any]): The query parameters for fetching tweets.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the fetched tweets.
        """
        try:
            tweets = self.client.get_users_tweets(id=user_id, **query_params)
            if tweets.data is None:
                return []
            return [tweet.data for tweet in tweets.data]
        except tweepy.errors.TooManyRequests as e:
            self.logger.error(f"Rate limit exceeded: Too Many Requests")
            reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + 15 * 60))
            wait_time = reset_time - int(time.time())
            self.logger.info(f"Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            return self._get_tweets_with_retries(user_id, query_params)
        except tweepy.TweepyException as e:
            self.logger.error(f"An error occurred: {e}")
            return []
