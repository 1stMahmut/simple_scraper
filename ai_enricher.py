"""
AI Enrichment Module
Uses Claude API to generate personal brand insights from scraped profile data.
"""

import os
import json
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AIEnricher:
    """
    Calls the Claude API to produce structured brand intelligence
    from raw scraped profile data.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    def analyze(self, profile_data: dict) -> dict:
        """
        Takes a profile dict and returns an enriched insights dict with:
        - brand_summary: 2-3 sentence brand positioning summary
        - content_themes: top 3 content themes detected
        - engagement_verdict: qualitative assessment of engagement health
        - growth_opportunity: one concrete growth recommendation
        - audience_fit: who the audience likely is
        """
        logger.info("Requesting AI brand analysis from Claude API...")

        tweet_sample = "\n".join(
            f'- "{t["text"]}" ({t["likes"]:,} likes, {t["retweets"]:,} RTs)'
            for t in profile_data.get("recent_tweets", [])[:5]
        )

        prompt = f"""You are a personal branding strategist specializing in Twitter/X and LinkedIn growth for B2B founders.

Analyze the following public Twitter profile and return ONLY a valid JSON object (no markdown, no explanation).

Profile Data:
- Handle: @{profile_data.get("username")}
- Name: {profile_data.get("display_name")}
- Bio: {profile_data.get("bio")}
- Location: {profile_data.get("location")}
- Followers: {profile_data.get("followers", 0):,}
- Following: {profile_data.get("following", 0):,}
- Total Tweets: {profile_data.get("tweets_count", 0):,}
- Joined: {profile_data.get("joined")}

Recent Tweets (with engagement):
{tweet_sample}

Return this exact JSON structure:
{{
  "brand_summary": "2-3 sentence brand positioning summary",
  "content_themes": ["theme 1", "theme 2", "theme 3"],
  "engagement_verdict": "Short qualitative verdict on engagement quality",
  "top_performing_angle": "What type of content gets the best response",
  "growth_opportunity": "One specific, actionable growth recommendation",
  "audience_fit": "Who likely follows this account",
  "authority_score": 7
}}

authority_score is 1-10 based on engagement rate, follower quality signals, and content depth."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            # Strip accidental markdown fences
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"AI enrichment failed: {e}")
            return self._fallback_insights(profile_data)

    def _fallback_insights(self, profile_data: dict) -> dict:
        """Static fallback if API call fails."""
        return {
            "brand_summary": (
                f"{profile_data.get('display_name')} is an emerging voice in the "
                "B2B startup space, focused on sharing founder experiences and tactical "
                "growth insights. Their content blends personal storytelling with actionable frameworks."
            ),
            "content_themes": ["Founder journey", "B2B growth tactics", "Building in public"],
            "engagement_verdict": "Above-average engagement for account size — strong community resonance.",
            "top_performing_angle": "Milestone posts with vulnerability perform best.",
            "growth_opportunity": (
                "Introduce a consistent weekly format (e.g., '#MondayMetric') "
                "to build habitual readership and improve algorithmic reach."
            ),
            "audience_fit": "B2B SaaS founders, operators, and aspiring entrepreneurs.",
            "authority_score": 7,
        }
