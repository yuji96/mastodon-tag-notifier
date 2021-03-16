# mastodon-tag-notifier

```
  __ __                    __           ___                     
 _\ \\ \__                /\ \__  __  /'___\ __                 
/\__  _  _\    ___     ___\ \ ,_\/\_\/\ \__//\_\     __   _ __  
\/_L\ \\ \L_ /' _ `\  / __`\ \ \/\/\ \ \ ,__\/\ \  /'__`\/\`'__\
  /\_   _  _\/\ \/\ \/\ \L\ \ \ \_\ \ \ \ \_/\ \ \/\  __/\ \ \/ 
  \/_/\_\\_\/\ \_\ \_\ \____/\ \__\\ \_\ \_\  \ \_\ \____\\ \_\ 
     \/_//_/  \/_/\/_/\/___/  \/__/ \/_/\/_/   \/_/\/____/ \/_/ 
```

mastodon-tag-notifier is a bot that notifies users who have assigned a hashtag in their settings when a hashtagged toot is posted.

## Description
You wouldn't wanna miss a toot with any hashtags that you interest.
Users only need to follow the bot and write interesting hashtags in their profile in order to be notified.

## Demo
### Screenshot
Screenshotting without personal information is a pain so I'll get to it later...

### User's setting in Mastodon
1. follow the bot.
2. Go to `settings page > Profile > Appearance > Profile metadata`, and set "Label" and "Content".
  - "Label": It must be as same as `tag-notifier` (which defined as [`self.search_field`][1]).
  - "Content": It's the hashtags you wanna receive notifications for. You can set multiple hashtags by separating them with spaces.

[1]: https://github.com/yuji96/mastodon-tag-notifier/blob/f41a3bdaffb94566c4e18bf0681e89bf87f77e1d/tag_notifier/listener.py#L38

example metadata:

|Label|Content|
|:--|:--| 
|tag-notifier|foo bar|

### Bot setting in Mastodon

1. Go to `settings page > Development`, and click "NEW APPLICATION".
2. Select the scope for read and write:statuses, and click "SUBMIT".


## Deploy (Heroku)
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
1. Click "Deploy to Heroku".
2. Set environment vars and so on.
3. In "Resources" tab, execute "Free Dynos".

## Requirement
Python3.8.0 or more

## Installation and Run the bot in local
```
$ git clone https://github.com/yuji96/mastodon-tag-notifier.git
$ cd mastodon-tag-notifier
$ pip install -e .
$ python tag_notofier/listerner.py
```




