# **NewsVerse**

Welcome to **NewsVerse**, a full-stack, AI-powered news aggregation and recommendation platform.  
This project ingests news from across the web, analyzes it using a sophisticated AI pipeline, and delivers personalized content to users through a modern web app and WhatsApp.

---

## ✅ **Project Architecture**

The project is built on a **decoupled monorepo structure**, containing three main parts:

1. **`frontend/`** – A modern React + TypeScript web application that serves as the primary user interface.
2. **`backend/`** – A Python-based microservice pipeline built with FastAPI and MongoDB—this is the core engine that scrapes, analyzes, and recommends articles.
3. **`Raw_code_developer/`** – A development sandbox containing initial experiments, tutorials (e.g., Crawl4ai), and sample datasets.

---

## ✅ **Overall Tech Stack**

| Area | Technology |
| :-- | :-- |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite |
| **Backend** | Python, FastAPI, MongoDB |
| **AI / ML** | LangChain/Custom Agents, SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Data Ingestion** | Crawl4ai, Custom Python (BeautifulSoup/Requests) |
| **Messaging** | Twilio API (WhatsApp) |

---

# ✅ **1. Frontend (`frontend/`)**

A responsive web application delivering full user experience.

### ✅ Technologies
- React
- TypeScript
- Tailwind CSS
- `shadcn/ui` components

### ✅ Key Pages & Features
- **`Homepage.tsx`** — Landing page showcasing featured articles & app features.
- **`News.tsx`** — Personalized news feed based on user recommendations.
- **`Login.tsx` / `Onboarding.tsx`** — Handles authentication & preference gathering.
- **`UserPreferences.tsx`** — Allows users to update interests; retrains preference profile.
- **`components/ArticleCard.tsx`** — Reusable UI card for displaying article summaries.

---

# ✅ **2. Backend (`backend/`)**

The backend is the **AI-driven brain** of the system, implemented as an asynchronous data pipeline.

---

## ✅ **Module 1: Scraping & Crawling**

**Directory:** `backend/Scraping_Crawling/`  
**Purpose:** Fetch raw articles (links, titles, content).

### ✅ Hybrid Strategy

1. **Broad Discovery — `Crawl4ai`**
   - Automatically discovers news articles across the web.

2. **Reliable Extraction — Custom Parsers**
   - For stable, major sources (BBC, CNN, HT, Benzinga), custom parser functions ensure consistency.

#### ✅ Conceptual Example (`parsers.py`)
```python
def parse_bbc(soup):
    """Custom parser for BBC News articles."""
    content = soup.find('article').text
    return content

def parse_cnn(soup):
    """Custom parser for CNN articles."""
    content = soup.find('div', class_='article__content').text
    return content

def parse_benzinga(soup):
    """Custom parser for Benzinga articles."""
    content = soup.find('div', class_='content-container').text
    return content

PARSER_MAP = {
    'bbc.com': parse_bbc,
    'cnn.com': parse_cnn,
    'hindustantimes.com': parse_ht,
    'benzinga.com': parse_benzinga
}

def get_parser_for_source(url):
    for domain, func in PARSER_MAP.items():
        if domain in url:
            return func
    return None
✅ Data Output Structure (MongoDB)
json
Copy code
{
  "_id": "67f1b9f3e4b0c8a2b5f8e1a2",
  "url": "https://www.bbc.com/news/world-politics-123456",
  "source": "BBC",
  "title": "Major Political Event Shakes Global Markets",
  "content": "Today, a significant political development occurred...",
  "date": "2025-11-08",
  "time": "12:30:00",
  "scraped_at": "2025-11-08T12:31:05Z",
  "processed_status": {
    "summarized": false,
    "fact_checked": false,
    "sentiment": false,
    "ner": false,
    "scored": false
  }
}
✅ Module 2: Article Processing Pipeline
Once raw articles are collected, a series of AI agents enrich the data.

✅ A. Summarization
Directory: backend/Summarization/

Agents: Summarization Agent

Example Prompt

css
Copy code
You are a professional news editor. Summarize the following news article into
3 key bullet points, followed by a concise 80-word paragraph.

Article:
{article_text}

Summary:
✅ B. Fact-Checker
Directory: backend/Fact_Checker/

Agents: Fact-Checking Agent

Example Prompt

pgsql
Copy code
Analyze the following article for factual accuracy. Identify the main claims.
Return a JSON:
1. "veracity_score": float (0.0–1.0)
2. "explanation": brief justification
✅ C. Sentiment Analysis
Directory: backend/Sentiment_Analysis/

Agents: Sentiment Agent

Example Prompt

arduino
Copy code
Classify article sentiment.
Respond as one word:
"Positive", "Negative", or "Neutral"
✅ D. Named Entity Recognition (NER)
Directory: backend/Name_Entity_Recognition/

Agents: NER Agent

Example Prompt

pgsql
Copy code
Extract all named entities.
Return JSON keys: "people", "organizations", "locations"
✅ Module 3: Embedding Creation
Directory: backend/Embedding_Creation/
Converts text into vector embeddings (e.g., 384-dim) for similarity matching.
Model: SentenceTransformer (all-MiniLM-L6-v2)

✅ Module 4: Article Scorer
Directory: backend/Article_Scorer/
Assigns a relevance/quality score per article.

✅ Example Formula (conceptual)
python
Copy code
llm_quality_score = agent_output      # 1–10
fact_check_score = article.fact_check.veracity_score  # 0–1

final_score = (w1 * llm_quality_score) + (w2 * fact_check_score)
✅ Module 5: Recommendation Engine
Directory: backend/Recommendation_Engine/
Matches users with most relevant articles.

✅ How it works
Converts user preferences → embedding

Computes cosine similarity to all article vectors

Returns top N results

python
Copy code
from sklearn.metrics.pairwise import cosine_similarity

similarity_scores = cosine_similarity(user_vector, all_article_vectors)
top_10_indices = similarity_scores[0].argsort()[-10:][::-1]
✅ Module 6: WhatsApp Messaging
Directory: backend/Whatsapp_Messaging/

Uses Twilio API to send messages

Scheduled via CRON jobs

Files:

whatsapp_sender.py

scheduler_tasks.py

✅ 3. Development Sandbox (Raw_code_developer/)
This directory contains:

Early prototypes

Notebook experiments

Crawl4ai tutorials

Sample datasets

e.g., BBC_filtered_news_articles.json

Initial Summarization / Fact-Check / Recommendation code

✅ How to Run the Project
✅ Prerequisites
Node.js ≥ 18

Python ≥ 3.10

MongoDB (local/cloud)

.env file with:

OpenAI key

Twilio key

MongoDB URI

✅ Backend Setup
bash
Copy code
cd backend
Create & activate virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate     # Mac/Linux
.\venv\Scripts\activate      # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Add API keys to .env

Run FastAPI Server:

bash
Copy code
uvicorn main:app --reload
Server runs at:
👉 http://localhost:8000

✅ Frontend Setup
bash
Copy code
cd frontend
Install dependencies:

bash
Copy code
npm install
Run Vite dev server:

bash
Copy code
npm run dev
App runs at:
👉 http://localhost:5173
