# Automatized Webhook for Birger

<img width="250px" src="birger.jpg"/>

This repository is created for Birger Discord Bot.

## Instructions :

You just need to change these line in config.json

```commandline
"webhooks_subs": [
    {
      "webhook_urls": "your-discord-server-webhook-url-here",
      "name": "reddit-community-name",
      "sort": "hot"
    },
```

Put your discord webhook webhook url for selected channel. [Server Settings > (Apps) Integrations > Webhooks > New Webhook > Copy webhook URL]

## For Forum Channels:
Use forum-webhook.py
```commandline
python forum-webhook.py
```

## For Text Channels:
Use webhook.py
```commandline
python webhook.py
```

Also dont forget to change delay in config.json

### Attention

If you set the duration to repeat too often you will get a timeout

```commandline
"delay": 100,
```