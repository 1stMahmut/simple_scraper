from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from dataclasses import asdict

from twitter_scraper import TwitterScraper
from airtable_sender import AirtableSender, AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE

import json
import urllib.request
import urllib.parse

app = Flask(__name__)
CORS(app)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip().lstrip("@")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        scraper = TwitterScraper(headless=True)
        profile = scraper.scrape(username)
        profile_dict = asdict(profile)

        sender = AirtableSender()
        result = sender.send(profile_dict)

        return jsonify({
            "success": True,
            "record_id": result.get("id"),
            "profile": {
                "username": profile.username,
                "display_name": profile.display_name,
                "followers": profile.followers,
                "following": profile.following,
                "bio": profile.bio,
                "recent_tweets": [
                    {
                        "text": t.text,
                        "likes": t.likes,
                        "retweets": t.retweets,
                        "replies": t.replies,
                    }
                    for t in profile.recent_tweets
                ],
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/records")
def records():
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{urllib.parse.quote(AIRTABLE_TABLE)}?sort%5B0%5D%5Bfield%5D=Name&sort%5B0%5D%5Bdirection%5D=asc"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {AIRTABLE_API_KEY}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        rows = [r["fields"] for r in data.get("records", [])]
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
