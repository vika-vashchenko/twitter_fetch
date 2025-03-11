from config.config_handler import JSONConfigHandler
from fetcher.twitter_post_fetcher import TwitterPostFetcher
from repository.user_repository import UserRepository
from main.twitter_puller import TwitterPuller

if __name__ == "__main__":
    config_handler = JSONConfigHandler()
    config = config_handler.load_config('config.json')
    post_fetcher = TwitterPostFetcher(config)
    user_repository = UserRepository('x_users.json', config)

    if config.get("use_mongodb"):
        user_repository.load_users_from_json()

    twitter_puller = TwitterPuller(config_handler, post_fetcher, user_repository)
    twitter_puller.run()
