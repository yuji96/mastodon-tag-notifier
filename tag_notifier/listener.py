from __future__ import annotations
from jinja2 import Template, Environment, FileSystemLoader
from mastodon import Mastodon, StreamListener
from typing import Tuple


def ignore_bot(method):
    def wrapper(obj, status: dict) -> None:
        if not status.get("account", {}).get("bot", True):
            return method(obj, status)
    return wrapper


def ignore_empty_tag(method):
    def wrapper(obj, status: dict) -> None:
        if status.get("tags"):
            return method(obj, status)
    return wrapper


class Listener(StreamListener):
    def __init__(self, client: Mastodon, bot_id: str,
                 ignore_sender: bool = True, debug: bool = False) -> None:
        super().__init__()
        self.client = client
        self.bot_id = bot_id
        self.search_field = "tag_notifier"
        self.ignore_sender = ignore_sender
        self.debug = debug

        env = Environment(loader=FileSystemLoader("tag_notifier"))
        self.template = template = env.get_template("status_template.j2")

    @ignore_bot
    @ignore_empty_tag
    def on_update(self, status: dict) -> None:
        sender_id = status.get("account", {}).get("id")
        tags = {tag.get("name") for tag in status.get("tags")}

        for acct, matched_tags in self.filter_followers(tags, sender_id):
            context = self.template.render(acct=acct, tags=matched_tags, url=status.get("url"))
            if self.debug:
                yield context
            else:
                mastodon.status_post(context, visibility="direct")

    def filter_followers(self, tags: set, sender_id: int) -> Tuple[str, set]:
        for acct in self.client.account_followers(self.bot_id):
            if self.ignore_sender and acct.get("id") == sender_id:
                print("ignore")
                continue
            if matched_tags := tags.intersection(self.get_assigned_tags(acct)):
                yield acct.get("acct"), matched_tags

    def get_assigned_tags(self, acct: dict) -> set:
        for field in acct.get("fields"):
            if field.get("name") == self.search_field:
                return set(field.get("value").split())
        return set()


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv(verbose=True)

    mastodon = Mastodon(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        access_token=os.environ["access_token"],
        api_base_url=os.environ["url"],
    )
    listener = Listener(mastodon, os.environ["bot_id"])
    mastodon.stream_public(listener)
