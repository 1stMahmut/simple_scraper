"""
Airtable Sender
Pushes a scraped TwitterProfile to an Airtable table.
"""

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE   = os.environ.get("AIRTABLE_TABLE", "Demo")


class AirtableSender:
    def __init__(self):
        self.api_key  = AIRTABLE_API_KEY
        self.base_id  = AIRTABLE_BASE_ID
        self.table    = AIRTABLE_TABLE
        self.endpoint = f"https://api.airtable.com/v0/{self.base_id}/{urllib.parse.quote(self.table)}"

    def send(self, profile: dict) -> dict:
        tweets_text = "\n\n".join(
            f'"{t["text"]}" — ♥{t["likes"]} ↺{t["retweets"]} 💬{t["replies"]}'
            for t in profile.get("recent_tweets", [])[:5]
        )

        fields = {
            "Name":          profile.get("username", ""),
            "Username":      profile.get("username", ""),
            "Display Name":  profile.get("display_name", ""),
            "Bio":           profile.get("bio", ""),
            "Location":      profile.get("location", ""),
            "Website":       profile.get("website", ""),
            "Joined":        profile.get("joined", ""),
            "Followers":     profile.get("followers", 0),
            "Following":     profile.get("following", 0),
            "Tweets Count":  profile.get("tweets_count", 0),
            "Verified":      profile.get("verified", False),
            "Avatar URL":    profile.get("avatar_url", ""),
            "Recent Tweets": tweets_text,
        }

        payload = json.dumps({"fields": fields}).encode("utf-8")

        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type":  "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                logger.info(f"Airtable record created: {result.get('id')}")
                return result
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            logger.error(f"Airtable error {e.code}: {body}")
            raise


