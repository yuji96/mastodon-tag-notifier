from pprint import pprint
from mastodon import Mastodon, StreamListener


def ignore_bot(method):
    def wrapper(obj, status):
        is_bot = status.get("account", {}).get("bot")
        if is_bot is None:
            raise ValueError
        if not is_bot:
            method(obj, status)
    return wrapper


class Listener(StreamListener):
    def __init__(self, client):
        super().__init__()
        self.client = client

    @ignore_bot
    def on_update(self, status):
        pprint(status)
        mastodon.status_post(
            f"@{os.environ['account']}\n{status.get('url')}",
            visibility="direct",
        )


if __name__ == "__main__":
    import os

    url = os.environ["url"]

    mastodon = Mastodon(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        access_token=os.environ["access_token"],
        api_base_url=url,
    )
    listener = Listener(mastodon)
    streamer = mastodon.stream_hashtag("test", listener)
