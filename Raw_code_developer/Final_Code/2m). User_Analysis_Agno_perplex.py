import json
import certifi
import re
from typing import Dict, List
from pymongo import MongoClient
from collections import Counter
from pydantic import BaseModel
from dotenv import load_dotenv

# External AI + Tools
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools

# -----------------------------------------------------------------------------
# 1. Data Models
# -----------------------------------------------------------------------------

class UserPreferenceAnalysis(BaseModel):
    user_id: str
    total_articles: int
    category_preferences: Dict[str, float]
    dominant_categories: List[str]
    sentiment_analysis: Dict[str, int]
    content_depth_preference: str
    geographic_interest: List[str]
    time_sensitivity: str
    detailed_summary: str


class CategoryBreakdown(BaseModel):
    category: str
    article_count: int
    percentage: float
    sample_titles: List[str]


# -----------------------------------------------------------------------------
# 2. MongoDB Connection
# -----------------------------------------------------------------------------

load_dotenv()
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())
db = client["UserDB"]
collection = db["UserCo"]


# -----------------------------------------------------------------------------
# 3. Analyzer Class
# -----------------------------------------------------------------------------

class UserPreferenceAnalyzer:
    def __init__(self):
        self.analysis_criteria = {
            "1_content_category": {
                "politics": ["trump", "election", "government", "politician", "parliament", "congress", "senate", "vote", "campaign", "political"],
                "technology": ["ai", "tech", "digital", "internet", "app", "software", "cyber", "innovation", "startup", "algorithm", "data"],
                "crime_justice": ["crime", "police", "arrest", "guilty", "court", "trial", "prison", "convicted", "assault", "murder"],
                "business_economy": ["business", "economy", "market", "stock", "finance", "company", "corporate", "trade", "economic", "financial"],
                "international": ["world", "global", "international", "foreign", "asia", "europe", "africa", "america", "war", "conflict"],
                "entertainment": ["movie", "music", "celebrity", "culture", "film", "concert", "entertainment", "show", "actor", "actress"],
                "health": ["health", "medical", "hospital", "doctor", "disease", "treatment", "medicine", "healthcare", "virus", "vaccine"],
                "sports": ["sports", "football", "basketball", "soccer", "tennis", "olympic", "team", "player", "game", "match"],
                "environment": ["climate", "environment", "green", "sustainability", "pollution", "energy", "nature", "conservation", "renewable"]
            },
            "2_sentiment_tone": {
                "positive": ["success", "achievement", "win", "victory", "celebration", "breakthrough", "improvement", "growth"],
                "negative": ["crisis", "disaster", "death", "attack", "violence", "scandal", "corruption", "failure"],
                "neutral": ["report", "study", "analysis", "meeting", "conference", "announcement", "statement", "update"]
            },
            "3_content_depth": {
                "breaking_news": ["breaking", "urgent", "just in", "developing", "live", "now", "alert"],
                "analysis": ["analysis", "explained", "investigation", "deep dive", "comprehensive", "detailed", "report"],
                "opinion": ["opinion", "editorial", "commentary", "perspective", "view", "debate", "discussion"]
            },
            "4_geographic_scope": {
                "local": ["city", "local", "community", "neighborhood", "municipal", "county", "state"],
                "national": ["country", "national", "federal", "nationwide", "domestic", "parliament", "congress"],
                "international": ["global", "world", "international", "foreign", "overseas", "cross-border", "worldwide"]
            },
            "5_time_sensitivity": {
                "real_time": ["live", "now", "breaking", "just", "minutes ago", "hours ago", "today"],
                "recent": ["yesterday", "this week", "recent", "latest", "current", "ongoing"],
                "historical": ["last year", "decade", "history", "past", "previous", "former", "archive"]
            }
        }

    def clean_title(self, title: str) -> str:
        """Remove timestamps and trailing info from titles."""
        cleaned = re.sub(r'\d+\s*hrs?\s*ago[A-Za-z\s&]*$', '', title)
        cleaned = re.sub(r'\d+[A-Za-z\s&]*$', '', cleaned)
        return cleaned.strip()

    def analyze_criteria(self, titles: List[str], criteria_type: str) -> Dict[str, int]:
        """Count how many titles match each category in the criteria."""
        scores = {}
        keywords_map = self.analysis_criteria[criteria_type]

        for category, keywords in keywords_map.items():
            count = 0
            for title in titles:
                title_lower = self.clean_title(title).lower()
                if any(keyword in title_lower for keyword in keywords):
                    count += 1
            scores[category] = count

        return scores

    def calculate_percentages(self, scores: Dict[str, int], total: int) -> Dict[str, float]:
        """Convert counts to percentages."""
        if total == 0:
            return {k: 0.0 for k in scores}
        return {k: round((v / total) * 100, 2) for k, v in scores.items()}

    def get_dominant_preferences(self, scores: Dict[str, int], top_n: int = 3) -> List[str]:
        """Get top scoring categories."""
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, score in sorted_items[:top_n] if score > 0]

    def extract_geographic_interests(self, titles: List[str]) -> List[str]:
        """Find countries/regions mentioned in titles."""
        geo_keywords = [
            "usa", "america", "uk", "britain", "china", "russia", "india", "japan", "germany",
            "france", "canada", "australia", "brazil", "mexico", "italy", "spain", "korea",
            "asia", "europe", "africa", "middle east", "latin america"
        ]
        found = {region for title in titles for region in geo_keywords if region in title.lower()}
        return list(found)[:5]


# -----------------------------------------------------------------------------
# 4. AI Agent Setup
# -----------------------------------------------------------------------------

analysis_agent = Agent(
    name="UserPreferenceAnalysisAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You are an expert user behavior analyst specializing in news consumption patterns. "
        "Analyze user reading preferences based on their article history and provide detailed insights."
    ),
    tools=[DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)


# -----------------------------------------------------------------------------
# 5. Main Execution
# -----------------------------------------------------------------------------

def main():
    analyzer = UserPreferenceAnalyzer()

    # Fetch user data
    users_data = [
        {"user_id": doc["user_id"], "title_list": [t.strip() for t in doc.get("title_list", []) if t.strip()]}
        for doc in collection.find({}, {"user_id": 1, "title_list": 1, "_id": 0})
        if "title_list" in doc and isinstance(doc["title_list"], list)
    ]

    if not users_data:
        raise ValueError("No users found in the collection.")

    all_results = []

    for user in users_data:
        uid = user["user_id"]
        titles = user["title_list"]

        print(f"\n🔍 Analyzing User: {uid} ({len(titles)} articles)")

        # Step 1: Content Categories
        cat_scores = analyzer.analyze_criteria(titles, "1_content_category")
        cat_pct = analyzer.calculate_percentages(cat_scores, len(titles))
        top_categories = analyzer.get_dominant_preferences(cat_scores)

        # Step 2: Sentiment
        sentiment_scores = analyzer.analyze_criteria(titles, "2_sentiment_tone")

        # Step 3: Depth
        depth_scores = analyzer.analyze_criteria(titles, "3_content_depth")
        depth_pref = analyzer.get_dominant_preferences(depth_scores, 1)
        depth_pref_str = depth_pref[0] if depth_pref else "mixed"

        # Step 4: Geography
        geo_interests = analyzer.extract_geographic_interests(titles)

        # Step 5: Time Sensitivity
        time_scores = analyzer.analyze_criteria(titles, "5_time_sensitivity")
        time_pref = analyzer.get_dominant_preferences(time_scores, 1)
        time_pref_str = time_pref[0] if time_pref else "mixed"

        # Step 6: AI Summary
        sample_titles = [analyzer.clean_title(t) for t in titles[:5]]
        prompt = f"""
        Analyze this user's news consumption:
        User: {uid}
        Total Articles: {len(titles)}
        Categories: {cat_pct}
        Top Categories: {top_categories}
        Sentiment: {sentiment_scores}
        Depth: {depth_pref_str}
        Time: {time_pref_str}
        Geo: {geo_interests}
        Sample Titles: {sample_titles}
        """
        try:
            ai_result = analysis_agent.run(prompt)
            summary = ai_result.content.strip()
        except Exception as e:
            summary = f"Could not generate AI summary: {e}"

        # Store result
        result = UserPreferenceAnalysis(
            user_id=uid,
            total_articles=len(titles),
            category_preferences=cat_pct,
            dominant_categories=top_categories,
            sentiment_analysis=sentiment_scores,
            content_depth_preference=depth_pref_str,
            geographic_interest=geo_interests,
            time_sensitivity=time_pref_str,
            detailed_summary=summary
        )
        all_results.append(result)

        # Save results to JSON file
    with open("user_preference_analysis.json", "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in all_results], f, indent=2, ensure_ascii=False)

    # Save results to MongoDB Atlas
    results_collection = db["UserPreferenceAnalysis"]
    results_collection.delete_many({})  # Optional: clear old analysis
    # Only store user_id and detailed_summary
    results_collection.insert_many([
        {"user_id": r.user_id, "detailed_summary": r.detailed_summary}
        for r in all_results
    ])


    print("\n✅ Analysis completed.")
    print(f"💾 Saved to user_preference_analysis.json and MongoDB ({len(all_results)} users)")


if __name__ == "__main__":
    main()