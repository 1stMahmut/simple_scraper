from flask import Flask, request, jsonify
from flask_cors import CORS
from dataclasses import asdict

from twitter_scraper import TwitterScraper
from airtable_sender import AirtableSender

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
            },
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
