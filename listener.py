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
    def __init__(self, client, bot_id):
        super().__init__()
        self.client = client
        self.bot_id = bot_id
        self.search_field = "tag_notifier"

    @ignore_bot
    def on_update(self, status):
        for tag in status.get("tags"):
            for acct in self.filter_followers(tag.get("name")):
                mastodon.status_post(
                    "\n".join([
                        f"@{acct}",
                        f"{status.get('url')}",
                    ]),
                    visibility="direct",
                )

    def filter_followers(self, tag):
        for acct in self.client.account_followers(self.bot_id):
            for field in acct.get("fields"):
                if field.get("name") == self.search_field and \
                        tag in field.get("value").split():
                    yield acct.get("acct")
                    break


if __name__ == "__main__":
    import os

    mastodon = Mastodon(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        access_token=os.environ["access_token"],
        api_base_url=os.environ["url"],
    )
    listener = Listener(mastodon, os.environ["bot_id"])
    streamer = mastodon.stream_public(listener)
