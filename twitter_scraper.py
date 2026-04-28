import json
import logging
import os
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")


@dataclass
class Tweet:
    text: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    date: str = ""


@dataclass
class TwitterProfile:
    username: str
    display_name: str = ""
    bio: str = ""
    location: str = ""
    website: str = ""
    joined: str = ""
    followers: int = 0
    following: int = 0
    tweets_count: int = 0
    recent_tweets: list[Tweet] = field(default_factory=list)
    avatar_url: str = ""
    verified: bool = False


class TwitterScraper:
    def __init__(self, headless: bool = True):
        self.api_key = RAPIDAPI_KEY

    def scrape(self, username: str) -> TwitterProfile:
        username = username.lstrip("@")
        logger.info(f"Fetching profile for @{username}")

        url = f"https://twitter-api45.p.rapidapi.com/screenname.php?screenname={username}"
        req = urllib.request.Request(
            url,
            headers={
                "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
                "x-rapidapi-key":  self.api_key,
            },
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        joined = ""
        if data.get("created_at"):
            try:
                dt = datetime.strptime(data["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
                joined = dt.strftime("%B %Y")
            except Exception:
                joined = data.get("created_at", "")

        return TwitterProfile(
            username=data.get("profile", username),
            display_name=data.get("name", ""),
            bio=data.get("desc", ""),
            location=data.get("location", ""),
            website=data.get("website", ""),
            joined=joined,
            followers=data.get("sub_count", 0),
            following=data.get("friends", 0),
            tweets_count=data.get("statuses_count", 0),
            avatar_url=data.get("avatar", ""),
            verified=data.get("blue_verified", False),
        )
