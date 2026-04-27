"""
PDF Report Generator
Produces a branded, professional Personal Brand Intelligence Report
from scraped profile data and AI insights.
"""

import logging
from dataclasses import asdict
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

logger = logging.getLogger(__name__)

# ── Brand Colors ──────────────────────────────────────────────────────────────
BLACK       = colors.HexColor("#0D0D0D")
WHITE       = colors.white
ACCENT      = colors.HexColor("#1DA1F2")   # Twitter blue
DARK_GRAY   = colors.HexColor("#2D2D2D")
MID_GRAY    = colors.HexColor("#6B7280")
LIGHT_GRAY  = colors.HexColor("#F3F4F6")
SUCCESS     = colors.HexColor("#10B981")
WARNING     = colors.HexColor("#F59E0B")


def _fmt(n: int) -> str:
    """Format large numbers cleanly: 47800 → '47.8K'"""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def _engagement_rate(profile_data: dict) -> float:
    """Avg engagement per tweet / followers * 100"""
    tweets = profile_data.get("recent_tweets", [])
    if not tweets or not profile_data.get("followers"):
        return 0.0
    avg_eng = sum(t["likes"] + t["retweets"] + t["replies"] for t in tweets) / len(tweets)
    return round((avg_eng / profile_data["followers"]) * 100, 2)


class PDFGenerator:
    """
    Generates a polished PDF report from profile data + AI insights.
    """

    PAGE_W, PAGE_H = A4
    MARGIN = 20 * mm

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_styles()

    def _register_styles(self):
        self.styles.add(ParagraphStyle(
            "ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=26,
            textColor=WHITE,
            spaceAfter=4,
            alignment=TA_LEFT,
        ))
        self.styles.add(ParagraphStyle(
            "ReportSubtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=colors.HexColor("#CBD5E1"),
            spaceAfter=0,
            alignment=TA_LEFT,
        ))
        self.styles.add(ParagraphStyle(
            "SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=BLACK,
            spaceBefore=14,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            "BodyText2",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK_GRAY,
            leading=15,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            "SmallLabel",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=MID_GRAY,
            spaceAfter=2,
        ))
        self.styles.add(ParagraphStyle(
            "TweetText",
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            textColor=DARK_GRAY,
            leading=14,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            "InsightText",
            fontName="Helvetica",
            fontSize=10,
            textColor=DARK_GRAY,
            leading=15,
            leftIndent=10,
            spaceAfter=5,
        ))

    def generate(self, profile_data: dict, insights: dict, output_path: str):
        logger.info(f"Generating PDF report → {output_path}")

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=self.MARGIN,
            leftMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=self.MARGIN,
        )

        story = []
        story += self._build_header(profile_data)
        story += self._build_metrics(profile_data)
        story += self._build_bio_section(profile_data)
        story += self._build_ai_insights(insights)
        story += self._build_tweets_section(profile_data)
        story += self._build_footer()

        doc.build(story)
        logger.info("PDF generated successfully.")

    # ── Section Builders ──────────────────────────────────────────────────────

    def _build_header(self, p: dict) -> list:
        username = p.get("username", "")
        display_name = p.get("display_name", username)
        handle = f"@{username}"
        generated = datetime.now().strftime("%B %d, %Y")

        # Dark header block via a 1-row table
        header_table = Table(
            [[
                Paragraph(display_name, self.styles["ReportTitle"]),
                Paragraph(f"Generated {generated}", ParagraphStyle(
                    "DateRight", fontName="Helvetica", fontSize=9,
                    textColor=colors.HexColor("#94A3B8"), alignment=TA_RIGHT,
                )),
            ]],
            colWidths=[120 * mm, 50 * mm],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLACK),
            ("TOPPADDING",    (0, 0), (-1, -1), 16),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
            ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ]))

        subtitle_row = Table(
            [[
                Paragraph(handle, ParagraphStyle(
                    "Handle", fontName="Helvetica-Bold", fontSize=12,
                    textColor=ACCENT, spaceAfter=0,
                )),
                Paragraph("PERSONAL BRAND INTELLIGENCE REPORT", ParagraphStyle(
                    "Tag", fontName="Helvetica-Bold", fontSize=8,
                    textColor=colors.HexColor("#94A3B8"), alignment=TA_RIGHT,
                )),
            ]],
            colWidths=[120 * mm, 50 * mm],
        )
        subtitle_row.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), DARK_GRAY),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))

        return [header_table, subtitle_row, Spacer(1, 10)]

    def _build_metrics(self, p: dict) -> list:
        eng_rate = _engagement_rate(p)
        followers_ratio = round(p.get("followers", 1) / max(p.get("following", 1), 1), 1)

        metrics = [
            ("FOLLOWERS",       _fmt(p.get("followers", 0)),    ACCENT),
            ("FOLLOWING",       _fmt(p.get("following", 0)),     MID_GRAY),
            ("TWEETS",          _fmt(p.get("tweets_count", 0)),  MID_GRAY),
            ("ENG. RATE",       f"{eng_rate}%",                  SUCCESS if eng_rate > 1 else WARNING),
            ("F/F RATIO",       f"{followers_ratio}x",           SUCCESS if followers_ratio > 5 else MID_GRAY),
        ]

        cells = []
        for label, value, color in metrics:
            cells.append(
                Table(
                    [
                        [Paragraph(label, self.styles["SmallLabel"])],
                        [Paragraph(f'<font color="#{color.hexval()[2:] if hasattr(color, "hexval") else "1DA1F2"}">{value}</font>',
                                   ParagraphStyle("MetricVal", fontName="Helvetica-Bold",
                                                  fontSize=20, textColor=color, spaceAfter=0))],
                    ],
                    colWidths=[34 * mm],
                )
            )

        metrics_table = Table([cells], colWidths=[34 * mm] * 5)
        metrics_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GRAY),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LINEAFTER",     (0, 0), (3, 0), 0.5, colors.HexColor("#E5E7EB")),
        ]))

        return [metrics_table, Spacer(1, 10)]

    def _build_bio_section(self, p: dict) -> list:
        elements = [Paragraph("Profile Overview", self.styles["SectionHeader"])]
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")))
        elements.append(Spacer(1, 6))

        if p.get("bio"):
            elements.append(Paragraph(p["bio"], self.styles["BodyText2"]))

        meta = []
        if p.get("location"):
            meta.append(f"📍 {p['location']}")
        if p.get("website"):
            meta.append(f"🔗 {p['website']}")
        if p.get("joined"):
            meta.append(f"📅 Joined {p['joined']}")

        if meta:
            elements.append(Paragraph("  ·  ".join(meta), ParagraphStyle(
                "Meta", fontName="Helvetica", fontSize=9, textColor=MID_GRAY, spaceAfter=6
            )))

        return elements

    def _build_ai_insights(self, insights: dict) -> list:
        elements = [Spacer(1, 6), Paragraph("AI Brand Analysis", self.styles["SectionHeader"])]
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")))
        elements.append(Spacer(1, 6))

        # Authority Score badge
        score = insights.get("authority_score", 7)
        score_color = SUCCESS if score >= 7 else (WARNING if score >= 5 else colors.HexColor("#EF4444"))
        score_table = Table(
            [[
                Paragraph(
                    f'<font color="#ffffff"><b>Authority Score: {score}/10</b></font>',
                    ParagraphStyle("Score", fontName="Helvetica-Bold", fontSize=11,
                                   textColor=WHITE, alignment=TA_CENTER)
                )
            ]],
            colWidths=[170 * mm],
        )
        score_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), score_color),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 8))

        # Insight rows
        insight_rows = [
            ("Brand Summary",           insights.get("brand_summary", "")),
            ("Top Performing Angle",    insights.get("top_performing_angle", "")),
            ("Engagement Verdict",      insights.get("engagement_verdict", "")),
            ("Audience Fit",            insights.get("audience_fit", "")),
            ("Growth Opportunity",      insights.get("growth_opportunity", "")),
        ]

        for label, value in insight_rows:
            if value:
                elements.append(Paragraph(label.upper(), self.styles["SmallLabel"]))
                elements.append(Paragraph(value, self.styles["InsightText"]))
                elements.append(Spacer(1, 4))

        # Content themes chips
        themes = insights.get("content_themes", [])
        if themes:
            elements.append(Paragraph("CONTENT THEMES", self.styles["SmallLabel"]))
            theme_cells = [[Paragraph(
                f'<font color="#ffffff"> {t} </font>',
                ParagraphStyle("Theme", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE)
            ) for t in themes]]
            widths = [max(30, len(t) * 5.5) * mm / 10 for t in themes]
            # Normalize to fit
            total = sum(widths)
            max_w = 170 * mm
            if total > max_w:
                widths = [w * (max_w / total) for w in widths]
            theme_table = Table(theme_cells, colWidths=widths)
            theme_table.setStyle(TableStyle([
                ("BACKGROUND",    (i, 0), (i, 0), ACCENT) for i in range(len(themes))
            ] + [
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("COLPADDING",    (0, 0), (-1, -1), 4),
            ]))
            elements.append(theme_table)

        return elements

    def _build_tweets_section(self, p: dict) -> list:
        tweets = p.get("recent_tweets", [])
        if not tweets:
            return []

        elements = [Spacer(1, 8), Paragraph("Recent Tweet Performance", self.styles["SectionHeader"])]
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")))
        elements.append(Spacer(1, 6))

        for tweet in tweets[:5]:
            text = tweet.get("text", "")
            likes = tweet.get("likes", 0)
            rts = tweet.get("retweets", 0)
            replies = tweet.get("replies", 0)

            stats_text = (
                f'<font color="#1DA1F2">♥ {_fmt(likes)}</font>  '
                f'<font color="#10B981">↺ {_fmt(rts)}</font>  '
                f'<font color="#6B7280">💬 {_fmt(replies)}</font>'
            )

            tweet_block = KeepTogether([
                Paragraph(f'"{text}"', self.styles["TweetText"]),
                Paragraph(stats_text, ParagraphStyle(
                    "TweetStats", fontName="Helvetica", fontSize=8.5,
                    textColor=MID_GRAY, spaceAfter=8
                )),
                HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#E5E7EB")),
                Spacer(1, 5),
            ])
            elements.append(tweet_block)

        return elements

    def _build_footer(self) -> list:
        return [
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB")),
            Paragraph(
                f"Generated by Profile Analyzer · {datetime.now().strftime('%Y-%m-%d %H:%M')} · Confidential",
                ParagraphStyle("Footer", fontName="Helvetica", fontSize=8,
                               textColor=MID_GRAY, alignment=TA_CENTER, spaceBefore=6)
            ),
        ]
