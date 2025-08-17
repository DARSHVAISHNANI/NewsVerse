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
    dominant_categories: List[str]
    sentiment_analysis: Dict[str, int]
    content_depth_preference: str
    geographic_interest: List[str]
    time_sensitivity: str
    ner_analysis: Dict[str, List[str]]   # NEW
    detailed_summary: str


# ----------------------------------------------------------------------------- 
# 2. MongoDB Connection
# -----------------------------------------------------------------------------
load_dotenv()
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())
db = client["UserDB"]
collection = db["UserCoUpdation"]


# ----------------------------------------------------------------------------- 
# 3. Analyzer Class
# -----------------------------------------------------------------------------
class UserPreferenceAnalyzer:
    def clean_title(self, title: str) -> str:
        """Remove timestamps and trailing info from titles."""
        cleaned = re.sub(r'\d+\s*hrs?\s*ago[A-Za-z\s&]*$', '', title)
        cleaned = re.sub(r'\d+[A-Za-z\s&]*$', '', cleaned)
        return cleaned.strip()

    def analyze_sentiment(self, titles: List[str]) -> Dict[str, int]:
        """Very light sentiment analysis via keywords (fallback)."""
        keywords = {
            "positive": ["success", "win", "victory", "growth", "celebration"],
            "negative": ["crisis", "death", "attack", "violence", "scandal"],
            "neutral": ["report", "study", "analysis", "meeting", "update"]
        }
        scores = {k: 0 for k in keywords}
        for title in titles:
            t = title.lower()
            for s, keys in keywords.items():
                if any(k in t for k in keys):
                    scores[s] += 1
        return scores

    def analyze_ner(self, ner_data: Dict[str, List[str]], top_n: int = 5) -> Dict[str, List[str]]:
        """Find top entities (persons, locations, organizations)."""
        result = {}
        for entity_type, entities in ner_data.items():
            if entities:
                counter = Counter(entities)
                top_entities = [ent for ent, _ in counter.most_common(top_n)]
                result[entity_type] = top_entities
            else:
                result[entity_type] = []
        return result

    def infer_categories_from_ner(self, ner_results: Dict[str, List[str]]) -> List[str]:
        """Infer user interest categories from NER rather than keywords."""
        categories = set()

        persons = ner_results.get("Person", [])
        orgs = ner_results.get("Organization", [])
        locs = ner_results.get("Location", [])

        # Example mappings
        if any(p in persons for p in ["Donald Trump", "Joe Biden", "Narendra Modi"]):
            categories.add("politics")
        if any(o in orgs for o in ["Foxconn", "Apple", "Google"]):
            categories.add("technology")
            categories.add("business_economy")
        if any(l in locs for l in ["Ukraine", "Russia", "USA", "China"]):
            categories.add("international")
        if any(o in orgs for o in ["Supreme Court", "Parliament", "Congress"]):
            categories.add("law_justice")
        if not categories:
            categories.add("general")

        return list(categories)


# ----------------------------------------------------------------------------- 
# 4. AI Agent Setup
# -----------------------------------------------------------------------------
analysis_agent = Agent(
    name="UserPreferenceAnalysisAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You are an expert user behavior analyst specializing in news consumption patterns. "
        "Base most of your analysis on NER entities (persons, organizations, locations). "
        "Use keywords only as secondary hints."
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

    users_data = [
        {
            "user_id": doc["user_id"],
            "title_list": [t.strip() for t in doc.get("title_list", []) if t.strip()],
            "ner": doc.get("NER", {})
        }
        for doc in collection.find({}, {"user_id": 1, "title_list": 1, "NER": 1, "_id": 0})
    ]

    if not users_data:
        raise ValueError("No users found in the collection.")

    all_results = []

    for user in users_data:
        uid = user["user_id"]
        titles = user["title_list"]
        ner_data = user.get("ner", {})

        print(f"\n🔍 Analyzing User: {uid} ({len(titles)} articles)")

        # Step 1: Sentiment (lightweight)
        sentiment_scores = analyzer.analyze_sentiment(titles)

        # Step 2: NER analysis
        ner_results = analyzer.analyze_ner(ner_data)

        # Step 3: Infer categories from NER
        dominant_categories = analyzer.infer_categories_from_ner(ner_results)

        # Step 4: Simple heuristics for depth & time
        depth_pref_str = "analysis" if len(titles) > 3 else "mixed"
        time_pref_str = "recent"

        # Step 5: AI Summary
        sample_titles = [analyzer.clean_title(t) for t in titles[:5]]
        prompt = f"""
        Analyze this user's news consumption:
        User: {uid}
        Total Articles: {len(titles)}
        Dominant Categories (from NER): {dominant_categories}
        Sentiment: {sentiment_scores}
        Depth: {depth_pref_str}
        Time: {time_pref_str}
        NER Highlights: {ner_results}
        Sample Titles: {sample_titles}
        """
        try:
            ai_result = analysis_agent.run(prompt)
            summary = ai_result.content.strip()
        except Exception as e:
            summary = f"Could not generate AI summary: {e}"

        result = UserPreferenceAnalysis(
            user_id=uid,
            total_articles=len(titles),
            dominant_categories=dominant_categories,
            sentiment_analysis=sentiment_scores,
            content_depth_preference=depth_pref_str,
            geographic_interest=ner_results.get("Location", []),
            time_sensitivity=time_pref_str,
            ner_analysis=ner_results,
            detailed_summary=summary
        )
        all_results.append(result)

    # Save results to JSON
    with open("NER_user_preference_analysis.json", "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in all_results], f, indent=2, ensure_ascii=False)

    # Save summaries to MongoDB
    results_collection = db["UserPreferenceAnalysisBasedNER"]
    results_collection.delete_many({})
    results_collection.insert_many([
        {"user_id": r.user_id, "detailed_summary": r.detailed_summary}
        for r in all_results
    ])

    print("\n✅ Analysis completed.")
    print(f"💾 Saved to user_preference_analysis.json and MongoDB ({len(all_results)} users)")


if __name__ == "__main__":
    main()