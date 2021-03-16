from __future__ import annotations
import logging
from typing import Callable, Iterator, Optional, Tuple

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from mastodon import Mastodon, StreamListener


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def ignore_bot(method: OnUpdateType) -> OnUpdateType:
    def wrapper(obj, status: dict) -> None:
        if status.get("account", {}).get("bot", True):
            logger.debug("Ignore bot toot")
            return None
        return method(obj, status)
    return wrapper


def ignore_empty_tag(method: OnUpdateType) -> OnUpdateType:
    def wrapper(obj, status: dict) -> None:
        if not status.get("tags"):
            logger.debug("Ignore toot without tag")
            return None
        return method(obj, status)
    return wrapper


class Listener(StreamListener):
    def __init__(self, client: Mastodon, bot_id: str,
                 ignore_sender: bool = True, debug: bool = False) -> None:
        super().__init__()
        self.client = client
        self.bot_id = bot_id
        self.search_field = "tag-notifier"
        self.ignore_sender = ignore_sender
        self.debug = debug

        env = Environment(loader=FileSystemLoader("tag_notifier"))
        self.raw = env.get_template("raw.j2")
        self.content = env.get_template("content.j2")

    @ignore_bot
    @ignore_empty_tag
    def on_update(self, status: dict) -> None:
        sender_id = status.get("account", {}).get("id")
        tags = {tag.get("name") for tag in status.get("tags", {})}
        logger.debug(f"{status.get('account', {}).get('acct')} toot with {tags}")
        for acct, matched_tags in self.filter_followers(tags, sender_id):
            logger.debug(f"{acct} will be notified about {matched_tags}")
            content = self.render_content(status, acct, matched_tags)
            if self.debug:
                logger.debug(content)
            else:
                mastodon.status_post(content, visibility="direct")

    def filter_followers(self, tags: set, sender_id: Optional[int]) -> Iterator[Tuple[str, set]]:
        for acct in self.client.account_followers(self.bot_id):
            if self.ignore_sender and acct.get("id") == sender_id:
                logger.debug("Ignore sender's own toot")
                continue
            if matched_tags := tags.intersection(self.get_assigned_tags(acct)):
                yield acct.get("acct"), matched_tags

    def get_assigned_tags(self, acct: dict) -> set:
        for field in acct.get("fields", {}):
            if field.get("name") == self.search_field:
                return set(field.get("value").split())
        return set()

    def render_content(self, status: dict, acct: str, tags: set) -> str:
        content = status.get("content", "").replace("<br />", "\n")
        body = BeautifulSoup(content, 'html.parser').get_text()
        raw = self.raw.render(acct=acct, tags=tags, url=status.get("url"), body=body)
        return self.content.render(raw=raw)


OnUpdateType = Callable[[Listener, dict], None]

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()

    mastodon = Mastodon(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        access_token=os.environ["access_token"],
        api_base_url=os.environ["url"],
    )
    listener = Listener(mastodon, os.environ["bot_id"])
    logger.debug("Start")
    mastodon.stream_public(listener)
