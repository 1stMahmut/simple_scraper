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

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(
            f"https://twitter-api45.p.rapidapi.com/{path}",
            headers={
                "x-rapidapi-host": "twitter-api45.p.rapidapi.com",
                "x-rapidapi-key":  self.api_key,
            },
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def scrape(self, username: str) -> TwitterProfile:
        username = username.lstrip("@")
        logger.info(f"Fetching profile for @{username}")

        profile_data  = self._get(f"screenname.php?screenname={username}")
        timeline_data = self._get(f"timeline.php?screenname={username}")

        joined = ""
        if profile_data.get("created_at"):
            try:
                dt = datetime.strptime(profile_data["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
                joined = dt.strftime("%B %Y")
            except Exception:
                joined = profile_data.get("created_at", "")

        tweets = []
        for t in timeline_data.get("timeline", [])[:10]:
            tweets.append(Tweet(
                text=t.get("text", ""),
                likes=t.get("favorites", 0),
                retweets=t.get("retweets", 0),
                replies=t.get("replies", 0),
                date=t.get("created_at", ""),
            ))

        return TwitterProfile(
            username=profile_data.get("profile", username),
            display_name=profile_data.get("name", ""),
            bio=profile_data.get("desc", ""),
            location=profile_data.get("location", ""),
            website=profile_data.get("website", ""),
            joined=joined,
            followers=profile_data.get("sub_count", 0),
            following=profile_data.get("friends", 0),
            tweets_count=profile_data.get("statuses_count", 0),
            avatar_url=profile_data.get("avatar", ""),
            verified=profile_data.get("blue_verified", False),
            recent_tweets=tweets,
        )
