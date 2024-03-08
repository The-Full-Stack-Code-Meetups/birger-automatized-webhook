from typing import List
import random
import datetime
import aiohttp
import asyncio
import colorama
import json
import sys
from datetime import datetime, timedelta
import requests

# Loading config.json
with open("config.json") as f:
    config = json.load(f)
    colors: List[str] = config["colors"]
    subreddits: List[str] = config["subreddits"]

    webhooks_data: List[str] = config["webhooks_subs"]

    user_agents: List[str] = config["user_agents"]
    webhook_url: str = config["webhook_url"]
    delay: int = config["delay"]
    ignored: List[str] = config["ignored"]
    sent_posts: List[str] = []


# Defining output function for better output readability
def output(type: str, message: str):
    if type == "warning":
        print(f"{colorama.Fore.YELLOW}[WARNING] {colorama.Fore.RESET} {message}")
    elif type == "error":
        print(f"{colorama.Fore.RED}[ERROR] {colorama.Fore.RESET} {message}")
    elif type == "success":
        print(f"{colorama.Fore.GREEN}[SUCCESS] {colorama.Fore.RESET} {message}")
    else:
        print(f"{colorama.Fore.CYAN}[INFO] {colorama.Fore.RESET} {message}")


def load_sent_posts():
    try:
        with open("sent_posts.txt") as f:
            # append each post id to the sent_posts list
            for post_id in f.read().split(" "):
                sent_posts.append(post_id)
    except FileNotFoundError:
        output("warning", "sent_posts.txt not found, creating it...")
        with open("sent_posts.txt", "w") as f:
            f.write("")


def save_sent_posts():
    with open("sent_posts.txt", "w") as f:
        f.write(" ".join(sent_posts))
    output("info", "Saved sent posts to sent_posts.txt")


async def get_posts(session: aiohttp.ClientSession, url: str):
    async with session.get(url, headers={"User-Agent": random.choice(user_agents)}) as response:
        if response.status == 200:
            data = await response.json()
            return random.choice(data["data"]["children"])["data"]
        else:
            output("error", f"Error getting posts: {response.status}")


async def send_post(webhooks_data: List[str]):
    async with aiohttp.ClientSession() as session:

        for subreddit in webhooks_data:
            post = await get_posts(session,
                                   f"https://www.reddit.com/r/{subreddit['name']}.json?sort={subreddit['sort']}")

            data_timestamp = datetime.fromtimestamp(post['created_utc']).isoformat()
            current_time = datetime.now().isoformat()
            if (datetime.fromisoformat(current_time) - datetime.fromisoformat(data_timestamp)) > timedelta(days=1):
                continue  # skip this post, it's older than 24 hours

            data = {
                "embeds": [
                    {
                        "title": post["title"],
                        "description": post["selftext"],
                        "url": f"https://www.reddit.com{post['permalink']}",
                        "color": random.choice(colors),
                        "image": {
                            # if the post is a video, use the video url
                            "url": post["url"] if post["is_video"] == False else post["media"]["reddit_video"][
                                "fallback_url"]
                        },
                        "timestamp": datetime.fromtimestamp(post["created_utc"]).isoformat(),
                        "footer": {
                            "text": f"Posted by u/{post['author']} in r/{subreddit['name']}"
                        },
                        "fields": [
                            {
                                "name": ":up: Score:",
                                "value": post["score"],
                                "inline": True
                            },
                            {
                                "name": ":speech_balloon: Comments:",
                                "value": post["num_comments"],
                                "inline": True
                            },
                            {
                                "name": ":underage: Is NSFW:",
                                "value": post["over_18"],
                                "inline": True
                            },
                            {
                                "name": ":link: Permanent link:",
                                "value": f"[Click here](https://www.reddit.com{post['permalink']})",
                                "inline": True
                            }
                        ]

                    }
                ]
            }

            if post["id"] in sent_posts:
                continue
            elif post["over_18"] == True and "nsfw" in ignored:
                continue
            elif post["stickied"] == True and "stickied" in ignored:
                continue
            elif post["locked"] == True and "locked" in ignored:
                continue
            elif post["spoiler"] == True and "spoiler" in ignored:
                continue
            elif post["pinned"] == True and "pinned" in ignored:
                continue
            elif post["archived"] == True and "archived" in ignored:
                continue
            # elif post["is_video"] == True and "video" in ignored:
            #    continue

            # wait the delay before sending the post
            await asyncio.sleep(delay)
            async with session.post(subreddit['webhook_urls'], json=data) as response:
                if response.status == 204:
                    output("success", f"Sent post: {post['title']}")
                    sent_posts.append(post["id"])
                else:
                    output("error", f"Error sending post: {response.status}")


async def main():
    if not webhook_url:
        output("error", "No webhook url provided, please add it to the config.json file and try again!")
        sys.exit(1)
    try:
        output("info", "=-=" * 20)
        load_sent_posts()
        output("info", "Subreddits: {}".format(", ".join([subreddit["name"] for subreddit in webhooks_data])))
        output("info", f"Delay: {delay}")
        output("info", "Webhook Url: {}".format(", ".join([subreddit["webhook_urls"] for subreddit in webhooks_data])))
        if ignored:
            output("info", f"Ignored: {', '.join(ignored)}")
        output("info", f"Found {len(sent_posts) - 1} sent posts" if len(sent_posts) > -1 else "No sent posts")
        output("info", "To stop the bot press CTRL+C")
        output("info", "=-=" * 20)
        while True:
            await send_post(webhooks_data)
    finally:
        save_sent_posts()


if __name__ == "__main__":
    asyncio.run(main())

