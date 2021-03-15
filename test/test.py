from mastodon import Mastodon
from tag_notifier.listener import Listener

status = dict(
    account=dict(id=0, acct="tester", bot=False),
    context="hoge #test",
    tags=[dict(name="test1")],
    url="<url>",
)

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
    listener = Listener(mastodon, bot_id=os.environ["bot_id"], debug=True)
    print(*list(listener.on_update(status)), sep="\n")
