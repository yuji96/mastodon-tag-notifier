from mastodon import Mastodon, StreamListener


def ignore_bot(method):
    def wrapper(obj, status):
        if not status.get("account", {}).get("bot", True):
            return method(obj, status)
    return wrapper


def ignore_empty_tag(method):
    def wrapper(obj, status):
        if status.get("tags"):
            return method(obj, status)
    return wrapper


class Listener(StreamListener):
    def __init__(self, client, bot_id):
        super().__init__()
        self.client = client
        self.bot_id = bot_id
        self.search_field = "tag_notifier"

    @ignore_bot
    @ignore_empty_tag
    def on_update(self, status):
        tags = {tag.get("name") for tag in status.get("tags")}

        for acct, matched_tags in self.filter_followers(tags):
            mastodon.status_post(
                "\n".join([
                    f"@{acct}",
                    f"{matched_tags}"
                    f"{status.get('url')}",
                ]),
                visibility="direct",
            )

    def filter_followers(self, tags):
        for acct in self.client.account_followers(self.bot_id):
            if matched_tags := tags.intersection(self.get_assigned_tags(acct)):
                yield acct.get("acct"), matched_tags

    def get_assigned_tags(self, acct):
        for field in acct.get("fields"):
            if field.get("name") == self.search_field:
                return set(field.get("value").split())
        return set()

    @staticmethod
    def join_hashtag(tags):
        return " ".join([f"#{tag}" for tag in tags])


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
