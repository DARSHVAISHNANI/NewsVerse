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
```

### ✅ Data Output Structure (MongoDB)
```json
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
```

---

## ✅ **Module 2: Article Processing Pipeline**

Once raw articles are collected, a series of AI agents enrich the data.

### ✅ **A. Summarization**

**Directory:** `backend/Summarization/`

**Agents:** Summarization Agent

**Example Prompt**
```
You are a professional news editor. Summarize the following news article into
3 key bullet points, followed by a concise 80-word paragraph.

Article:
{article_text}

Summary:
```

### ✅ **B. Fact-Checker**

**Directory:** `backend/Fact_Checker/`

**Agents:** Fact-Checking Agent

**Example Prompt**
```
Analyze the following article for factual accuracy. Identify the main claims.
Return a JSON:
1. "veracity_score": float (0.0–1.0)
2. "explanation": brief justification
```

### ✅ **C. Sentiment Analysis**

**Directory:** `backend/Sentiment_Analysis/`

**Agents:** Sentiment Agent

**Example Prompt**
```
Classify article sentiment.
Respond as one word:
"Positive", "Negative", or "Neutral"
```

### ✅ **D. Named Entity Recognition (NER)**

**Directory:** `backend/Name_Entity_Recognition/`

**Agents:** NER Agent

**Example Prompt**
```
Extract all named entities.
Return JSON keys: "people", "organizations", "locations"
```

---

## ✅ **Module 3: Embedding Creation**

**Directory:** `backend/Embedding_Creation/`  
Converts text into vector embeddings (e.g., 384-dim) for similarity matching.  
**Model:** SentenceTransformer (`all-MiniLM-L6-v2`)

---

## ✅ **Module 4: Article Scorer**

**Directory:** `backend/Article_Scorer/`  
Assigns a relevance/quality score per article.

### ✅ Example Formula (conceptual)
```python
llm_quality_score = agent_output      # 1–10
fact_check_score = article.fact_check.veracity_score  # 0–1

final_score = (w1 * llm_quality_score) + (w2 * fact_check_score)
```

---

## ✅ **Module 5: Recommendation Engine**

**Directory:** `backend/Recommendation_Engine/`  
Matches users with most relevant articles using a sophisticated multi-stage pipeline that combines user behavior analysis, AI-powered profile generation, and vector similarity matching.

---

### ✅ **The Recommendation Pipeline: Complete Flow**

The recommendation system follows a precise, multi-step process that transforms raw user interactions into personalized article recommendations.

---

#### **🔹 Trigger: User Interaction**

The pipeline begins when a user performs an action in the frontend:

- **Liking an article** (via `ArticleCard.tsx`)
- **Defining interests** in their profile (via `UserPreferences.tsx`)

These actions are logged in MongoDB, creating records of:
- `liked_article_ids` — List of articles the user has interacted with
- `explicit_preferences` — Raw text preferences (e.g., "I like AI and finance")

---

#### **🔹 Step 1: User Analysis (`user_analyzer.py`)**

When a recommendation is needed, this script creates a unified "profile" of the user's interests.

**Process:**
1. Fetches two data sources from MongoDB:
   - The user's `liked_article_ids`
   - The user's `explicit_preferences` (raw text)
2. Retrieves the full text content (or summaries) of all liked articles
3. Collects all preference data into a single dataset

**Output:** A collection of raw, "noisy" text data (e.g., 5 liked articles + 3 preference phrases)

---

#### **🔹 Step 2: The Analysis Agent (`agents.py`)**

The raw user data is processed by an AI agent to distill it into a clean, meaningful profile.

**Agent:** User Analyzer Agent (defined in `backend/Recommendation_Engine/agents.py`)

**Example Prompt:**
```
You are a user profile analyzer. Based on the following articles a user has liked 
({liked_article_content}) and their stated interests ({explicit_preferences}), 
generate a single, dense paragraph that summarizes this user's true, nuanced interests. 
Identify key topics, entities, and recurring themes.
```

**Example Transformation:**

**Input:**
- Article on Tesla
- Article on NVIDIA stock
- Preference: "AI"

**Agent Output:**
> "This user is interested in high-growth technology, specifically in the electric vehicle and artificial intelligence sectors. They follow key companies like Tesla and NVIDIA, and are interested in the financial market implications of new tech."

**Result:** A single, high-quality "interest paragraph" that captures the user's true preferences.

---

#### **🔹 Step 3: Profile Vectorization (`embeddings.py`)**

The clean "interest paragraph" from Step 2 is converted into a mathematical representation.

**Process:**
1. The interest paragraph is fed into the embedding model (from `backend/Embedding_Creation/embeddings.py`)
2. Uses SentenceTransformer (`all-MiniLM-L6-v2`) to generate vector embeddings
3. Output: A single **User Profile Vector** (e.g., a `[1, 384]` array)

**Storage:** This vector is saved in the user's MongoDB document for quick retrieval, avoiding recomputation on every request.

---

#### **🔹 Step 4: The Final Recommendation (`article_recommender.py`)**

This is the core matching engine, triggered by:
- Frontend requests (from `News.tsx`)
- WhatsApp service (from `whatsapp_sender.py`)

**Process:**

1. **Fetch User Profile Vector**
   - Retrieves the pre-calculated User Profile Vector from MongoDB

2. **Load Article Vectors**
   - Loads all Article Vectors from the database (created by `Embedding_Creation/embeddings.py` when articles were first scraped)

3. **Calculate Similarity**
   - Uses cosine similarity to compute the mathematical "closeness" between the User Profile Vector and all Article Vectors

**Code Implementation:**
```python
from sklearn.metrics.pairwise import cosine_similarity

# user_vector.shape is [1, 384]
# all_article_vectors.shape is [N, 384] (N = number of articles)

# This calculates the similarity of the user to EVERY article
similarity_scores = cosine_similarity(user_vector, all_article_vectors)
# Result is an array like: [0.91, 0.23, 0.88, 0.05, ...]
```

---

#### **🔹 Step 5: Ranking and Delivery**

The final step sorts and delivers the most relevant articles.

**Process:**
1. Sorts the `similarity_scores` array from highest to lowest
2. Takes the **Top 10** article IDs from this sorted list
3. Returns the final list as a JSON response to the frontend
4. Frontend displays these articles to the user in `News.tsx`

**Result:** Users receive personalized article recommendations that match their interests, behavior, and stated preferences.

---

### ✅ **Key Files in Recommendation Engine**

- **`user_analyzer.py`** — Analyzes user behavior and preferences
- **`agents.py`** — Contains the User Analyzer Agent (LLM-based profile generation)
- **`article_recommender.py`** — Core matching engine using cosine similarity
- **`engine.py`** — Orchestrates the recommendation pipeline
- **`model_loader.py`** — Loads embedding models for vectorization

---

## ✅ **Module 6: WhatsApp Messaging**

**Directory:** `backend/Whatsapp_Messaging/`

- Uses Twilio API to send messages
- Scheduled via CRON jobs

**Files:**
- `whatsapp_sender.py`
- `scheduler_tasks.py`

---

# ✅ **3. Development Sandbox (`Raw_code_developer/`)**

This directory contains:

- Early prototypes
- Notebook experiments
- Crawl4ai tutorials
- Sample datasets
  - e.g., `BBC_filtered_news_articles.json`
- Initial Summarization / Fact-Check / Recommendation code

---

# ✅ **How to Run the Project**

## ✅ **Prerequisites**

- Node.js ≥ 18
- Python ≥ 3.10
- MongoDB (local/cloud)
- `.env` file with:
  - OpenAI key
  - Twilio key
  - MongoDB URI

---

## ✅ **Backend Setup**

```bash
cd backend
```

### Create & activate virtual environment:

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Add API keys to `.env`

### Run FastAPI Server:

```bash
uvicorn main:app --reload
```

**Server runs at:**  
👉 http://localhost:8000

---

## ✅ **Frontend Setup**

```bash
cd frontend
```

### Install dependencies:

```bash
npm install
```

### Run Vite dev server:

```bash
npm run dev
```

**App runs at:**  
👉 http://localhost:5173

---

## 📝 **License**

See [LICENSE](LICENSE) file for details.
