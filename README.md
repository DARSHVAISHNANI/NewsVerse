<div align="center">

# 📰 **NewsVerse**

### *AI-Powered News Aggregation & Recommendation Platform*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

**A sophisticated full-stack platform that ingests news from across the web, analyzes it using AI agents, and delivers personalized content through a modern web app and WhatsApp.**

[Features](#-key-features) • [Architecture](#-project-architecture) • [Installation](#-how-to-run-the-project) • [Documentation](#-module-documentation)

</div>

---

## 📋 **Table of Contents**

- [✨ Key Features](#-key-features)
- [🏗️ Project Architecture](#️-project-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📚 Module Documentation](#-module-documentation)
  - [Module 1: Scraping & Crawling](#-module-1-scraping--crawling)
  - [Module 2: Article Processing Pipeline](#-module-2-article-processing-pipeline)
  - [Module 3: Embedding Creation](#-module-3-embedding-creation)
  - [Module 4: Article Scorer](#-module-4-article-scorer)
  - [Module 5: Recommendation Engine](#-module-5-recommendation-engine)
  - [Module 6: WhatsApp Messaging](#-module-6-whatsapp-messaging)
- [💾 Database Schema](#-database-schema--format)
- [🚀 How to Run the Project](#-how-to-run-the-project)
- [📖 API Documentation](#-api-documentation)
- [🔧 Development](#-development-sandbox)

---

## ✨ **Key Features**

### 🤖 **AI-Powered Analysis**
- **Dual Summarization**: Professional factual summaries + child-friendly story formats
- **Fact-Checking**: Web-search verified claims with boolean verdicts
- **Sentiment Analysis**: Positive/Negative/Neutral classification with reasoning
- **Named Entity Recognition**: Extracts Person, Location, Organization entities

### 🎯 **Personalized Recommendations**
- **Behavioral Analysis**: Learns from user interactions and preferences
- **Vector Similarity Matching**: Cosine similarity-based article recommendations
- **Real-time Updates**: Dynamic preference profile generation
- **Top 10 Curation**: Delivers most relevant articles per user

### 📱 **Multi-Channel Delivery**
- **Modern Web App**: React + TypeScript frontend with Tailwind CSS
- **WhatsApp Integration**: Scheduled personalized news delivery via Twilio
- **Responsive Design**: Optimized for all devices

### 🔄 **Resilient Architecture**
- **API Failover**: Automatic Gemini → Groq switching on rate limits
- **Deduplication**: Smart article grouping to avoid redundant processing
- **Hybrid Scoring**: Combines AI analysis (60%) with user feedback (40%)
- **Comprehensive Logging**: MongoDB + local JSON file backups

---

## 🏗️ **Project Architecture**

The project is built on a **decoupled monorepo structure**, containing three main parts:

```
NewsVerse/
├── 📱 frontend/              # React + TypeScript web application
├── ⚙️  backend/              # Python microservice pipeline
│   ├── Scraping_Crawling/
│   ├── Summarization/
│   ├── Fact_Checker/
│   ├── Sentiment_Analysis/
│   ├── Name_Entity_Recognition/
│   ├── Embedding_Creation/
│   ├── Article_Scorer/
│   ├── Recommendation_Engine/
│   └── Whatsapp_Messaging/
└── 🧪 Raw_code_developer/   # Development sandbox & experiments
```

### **Data Flow**

```
Web Sources → Scraping → Processing Pipeline → Embeddings → Scoring → Recommendations → Users
                ↓              ↓                    ↓            ↓            ↓
            MongoDB      AI Agents          Vector DB    Quality    Personalized
                                                          Scores      Feed
```

---

## 🛠️ **Tech Stack**

| Area | Technology |
| :-- | :-- |
| **Frontend** | React 18+, TypeScript, Tailwind CSS, Vite, shadcn/ui |
| **Backend** | Python 3.10+, FastAPI, MongoDB, APScheduler |
| **AI Framework** | **[Agno Framework](https://github.com/agno-ai/agno)** - Agent orchestration & LLM integration |
| **AI / ML** | LangChain, SentenceTransformers (`all-MiniLM-L6-v2`), scikit-learn |
| **LLM Providers** | Google Gemini (Primary), Groq (Failover via Agno) |
| **Data Ingestion** | Crawl4ai, BeautifulSoup, Requests |
| **Messaging** | Twilio API (WhatsApp) |
| **Authentication** | Google OAuth 2.0 |
| **Vector Database** | MongoDB (embedding storage) |
| **Task Scheduling** | APScheduler (CRON jobs) |

### **Key Technologies Explained**

#### **🤖 Agno Framework**
[Agno](https://github.com/agno-ai/agno) is a powerful Python framework for building AI agents. In NewsVerse, we use Agno to:
- Create specialized AI agents (Summarization, Fact-Checking, Sentiment Analysis, NER, Article Scoring)
- Handle LLM provider management (Gemini, Groq)
- Implement automatic API failover mechanisms
- Orchestrate multi-agent workflows

> **Special Thanks:** This project is built using the Agno Framework created by **Ashpreet B.** (CEO of Agno). The framework's agent-based architecture made it seamless to build and manage multiple AI agents for different tasks.

#### **⚡ FastAPI**
High-performance Python web framework used for:
- RESTful API endpoints
- User authentication (Google OAuth)
- Background task scheduling
- Pipeline orchestration endpoints

#### **🎨 React + TypeScript**
Modern frontend stack providing:
- Type-safe component development
- Responsive UI with Tailwind CSS
- Real-time article recommendations
- User preference management

#### **💾 MongoDB**
Document database storing:
- Articles with embeddings
- User profiles and preferences
- Recommendation cache
- Processing status tracking

---

## 📚 **Module Documentation**

### ✅ **Module 1: Scraping & Crawling**

**Directory:** `backend/Scraping_Crawling/`  
**Purpose:** Fetch raw articles (links, titles, content) from multiple news sources.

#### **Hybrid Strategy**

1. **🌐 Broad Discovery — `Crawl4ai`**
   - Automatically discovers news articles across the web
   - Handles dynamic content and JavaScript-rendered pages

2. **🎯 Reliable Extraction — Custom Parsers**
   - For stable, major sources (BBC, CNN, HT, Benzinga), custom parser functions ensure consistency
   - Handles source-specific HTML structures

#### **Conceptual Example (`parsers.py`)**

```python
def parse_bbc(soup):
    """Custom parser for BBC News articles."""
    content = soup.find('article').text
    return content

def parse_cnn(soup):
    """Custom parser for CNN articles."""
    content = soup.find('div', class_='article__content').text
    return content

PARSER_MAP = {
    'bbc.com': parse_bbc,
    'cnn.com': parse_cnn,
    'hindustantimes.com': parse_ht,
    'benzinga.com': parse_benzinga
}
```

#### **Data Output Structure (MongoDB)**

```json
{
  "_id": "HT_20250908_141827_5388",
  "source": "HT",
  "title": "Vice-president election on Sept 9...",
  "date": "2025-09-08",
  "time": "13:43:25",
  "content": "The stage is set for...",
  "url": "https://www.hindustantimes.com/...",
  "scraped_at": "2025-09-08T14:18:27.311+00:00",
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

### ✅ **Module 2: Article Processing Pipeline**

Once raw articles are collected, a series of AI agents enrich the data. All modules feature resilient API handling with automatic failover from Gemini to Groq when rate limits are encountered.

---

#### **🔹 A. Summarization**

**Directory:** `backend/Summarization/`  
**Agents Used:** 2 (Summarization Agent, Story Agent)

**Purpose:** Generates two types of summaries for each article:
1. **Factual Summary** — Concise, professional summary (2-4 sentences)
2. **Story Summary** — Child-friendly, engaging story format (3-5 sentences, ages 6-12)

**How it Works (`run_summarization.py`):**

1. **Fetch Articles:** Retrieves articles from MongoDB that need summarization
2. **Generate Factual Summary:** Calls `get_factual_summary()` which:
   - Uses the Summarization Agent (Groq model: `openai/gpt-oss-120b`)
   - Handles API failover (Gemini → Groq on rate limits)
   - Returns JSON with `summary` field
3. **Generate Story Summary:** Calls `get_story_summary()` which:
   - Uses the Story Agent (Groq model: `openai/gpt-oss-120b`)
   - Creates child-friendly summaries with simple language
   - Returns JSON with `story_summary` field
4. **Update Database:** Saves both summaries to the article document

**Agent Prompts (`agents.py`):**

**Summarization Agent:**
```
You are a news article summarizer. Summarize the given article text in 2-4 sentences.

Return JSON in this exact format:
{
    "summary": "<short, concise summary of the article>"
}

Do NOT include anything outside the JSON object.
```

**Story Agent:**
```
You are a children's story writer. Read the article carefully and summarize it in a fun, 
simple, and easy-to-read way for kids.

Rules:
1. Use simple language suitable for 6-12 year old children.
2. Make it engaging like a short story.
3. Keep the summary concise (3-5 sentences max).
4. Focus on the main events or important points, but avoid technical jargon.
5. Return JSON in this exact format:
{
    "story_summary": "<summary written as a story for kids>"
}
6. Do NOT include anything outside the JSON object.
```

**Output Format:**
```json
{
  "summarization": {
    "summary": "Concise factual summary...",
    "story_summary": "Child-friendly story format..."
  }
}
```

---

#### **🔹 B. Fact-Checker**

**Directory:** `backend/Fact_Checker/`**  
**Agents Used:** 1 (Fact-Checker Agent with Web Search Tools)

**Purpose:** Verifies factual claims in articles using web search tools and returns a boolean verdict.

**How it Works (`fact_checker.py`):**

1. **Fetch Articles:** Retrieves all articles from MongoDB
2. **Extract Main Claim:** The agent identifies the primary factual claim
3. **Web Search Verification:** Uses ONE of the following tools:
   - `DuckDuckGoTools`
   - `GoogleSearchTools`
   - `WebBrowserTools`
   - `WebsiteTools`
4. **Compare Results:** Compares claim against top 3 reputable sources (BBC, Reuters, AP, Bloomberg, etc.)
5. **Generate Verdict:** Returns boolean result with explanation
6. **Update Database:** Saves fact-check results to article document
7. **Save Local Copy:** Writes results to `fact_check_results.json`

**Agent Instructions (`agents.py`):**
```
Step 1: Read the provided news article text.
Step 2: Extract the main factual claim from the article.
Step 3: Use ONLY ONE search (DuckDuckGo, GoogleSearch, WebBrowser, or WebsiteTools) for that claim.
Step 4: Compare the claim to the top 3 reputable search results (BBC, Reuters, AP, Bloomberg, etc.).
Step 5: Decide if the claim is factually correct (true or false).
Step 6: Output the result ONLY in a raw JSON object (no markdown block or surrounding text). 
The JSON MUST have exactly two fields: 'llm_verdict' (boolean: true/false) and 
'fact_check_explanation' (string: short reason).

Example: {"llm_verdict": true, "fact_check_explanation": "The claim is supported by multiple reputable sources."}
```

**Output Format:**
```json
{
  "fact_check": {
    "llm_verdict": false,
    "fact_check_explanation": "The article claims that Jagdeep Dhankhar resigned as Vice President on..."
  }
}
```

**Features:**
- ✅ **API Failover:** Automatically switches from Gemini to Groq on rate limits
- ✅ **Tool-Based Verification:** Uses real web search to verify claims
- ✅ **Reputable Source Focus:** Prioritizes trusted news sources for verification

---

#### **🔹 C. Sentiment Analysis**

**Directory:** `backend/Sentiment_Analysis/`  
**Agents Used:** 1 (Sentiment Agent)

**Purpose:** Classifies article sentiment as Positive, Negative, or Neutral with reasoning.

**How it Works (`sentiment.py`):**

1. **Fetch Articles:** Retrieves articles that need sentiment analysis
2. **Analyze Content:** Agent analyzes tone and language
3. **Classify Sentiment:** Returns classification with reason
4. **Update Database:** Saves sentiment to article document
5. **Save Local Copy:** Writes results to `sentiment_analysis.json`

**Agent Instructions (`agents.py`):**
```
You are a sentiment evaluation agent. Analyze the tone and language of the article text.  
Determine sentiment strictly as **Positive, Negative, or Neutral** based on these rules:

1. **Positive** → The article contains positive keywords (e.g., growth, profit, gain, recovery, 
   expansion, strong, successful), or the overall tone is optimistic and confidence-building.  
2. **Negative** → The article contains negative keywords (e.g., loss, decline, fall, risk, weak, 
   downgrade, failure), or the overall tone is pessimistic, warning, or confidence-reducing.  
3. **Neutral** → The article is mainly factual, descriptive, or balanced — with no clear 
   positive or negative tone. Includes objective reporting, announcements, or mixed signals.  
4. Return only JSON in this exact format:

{
    "sentiment": "<Positive|Negative|Neutral>",
    "reason": "<short reason explaining the classification>"
}

5. Reason should be brief (1-2 sentences).  
6. Do NOT include anything outside the JSON object.
```

**Output Format:**
```json
{
  "sentiment": "Neutral"
}
```

**Features:**
- ✅ **API Failover:** Automatically switches from Gemini to Groq on rate limits
- ✅ **Detailed Classification:** Provides reasoning for sentiment classification
- ✅ **Keyword-Based Analysis:** Uses keyword detection and tone analysis

---

#### **🔹 D. Named Entity Recognition (NER)**

**Directory:** `backend/Name_Entity_Recognition/`  
**Agents Used:** 1 (NER Agent)

**Purpose:** Extracts and aggregates named entities (Person, Location, Organization) from all articles a user has liked, storing them in the user's profile.

**How it Works (`NER.py`):**

1. **Fetch Users:** Retrieves all users from the user collection
2. **Get User's Liked Articles:** For each user, retrieves their `title_id_list` (articles they've interacted with)
3. **Process Each Article:** For each article in the user's list:
   - Fetches article content from the article collection
   - Runs NER agent on the content
   - Extracts entities (Person, Location, Organization)
4. **Aggregate Entities:** Combines all entities from all user's articles into a single aggregated list (removes duplicates)
5. **Update User Profile:** Saves aggregated entities to the user's `ner_data` field in MongoDB

**Agent Instructions (`agents.py`):**
```
Extract all unique named entities from the following news article text and categorize them 
as "Person", "Location" (including cities/countries/regions), or "Organization" 
(companies, institutions). 

Return strictly a JSON object in this format:
{
  "Person": [list of unique person names],
  "Location": [list of unique locations],
  "Organization": [list of unique organizations]
}

Do not include any other text, comments, or explanations. Return valid JSON only.
```

**Output Format (in User Collection):**
```json
{
  "ner_data": {
    "Person": ["Rohit Arya", "Deepak Kesarkar", "Ashish Shelar", ...],
    "Location": ["Mumbai", "Pune", "Maharashtra", ...],
    "Organization": ["BCCI", "School Education Department", ...]
  }
}
```

**Key Features:**
- ✅ **User-Centric:** Processes entities per user, not per article
- ✅ **Aggregation:** Combines entities from all user's liked articles
- ✅ **Deduplication:** Removes duplicate entities automatically
- ✅ **Profile Building:** Used to build user interest profiles for recommendations

> **Note:** This module updates the **User Collection**, not the Article Collection, as it builds user preference profiles based on their reading history.

---

### ✅ **Module 3: Embedding Creation**

**Directory:** `backend/Embedding_Creation/`  
**Purpose:** Converts article text into high-dimensional vector embeddings for semantic similarity matching.

**How it Works (`embeddings.py`):**

1. **Connect to Database:** Establishes connection to MongoDB article collection
2. **Fetch Unprocessed Articles:** Retrieves articles that don't have embeddings yet
3. **Generate Embeddings:** For each article:
   - Combines `title` and `content` for richer context
   - Uses SentenceTransformer model (`all-MiniLM-L6-v2`)
   - Generates 384-dimensional vector embedding
   - Converts to list format for MongoDB storage
4. **Update Database:** Saves embedding array to article document
5. **Logging:** Tracks progress and errors for each article

**Model Details:**
- **Model:** `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimensions:** 384
- **Purpose:** Semantic similarity matching for recommendations
- **Input:** Article title + content (combined text)
- **Output:** Vector array stored in `embedding` field

**Code Example:**
```python
from Embedding_Creation.model_loader import embedding_model

# Combine title and content for richer embedding
text_to_embed = f"{article.get('title', '')} {article.get('content', '')}"

# Generate the embedding
embedding = embedding_model.encode(text_to_embed).tolist()

# Store in MongoDB
db_manager.updateArticleEmbedding(collection, article["_id"], embedding)
```

**Key Features:**
- ✅ **Efficient Processing:** Only processes articles without embeddings
- ✅ **Rich Context:** Combines title and content for better semantic representation
- ✅ **Batch Processing:** Handles multiple articles efficiently
- ✅ **Error Resilience:** Continues processing even if individual articles fail

---

### ✅ **Module 4: Article Scorer**

**Directory:** `backend/Article_Scorer/`  

**Purpose:** This module assigns a hybrid "quality" score to each article by combining an AI-generated "knowledge depth" score with a (potential) user-provided score. It is designed to be resilient, with a built-in failover from the Gemini API to Groq.

**Agents Used:** 1 (The Article Scoring Agent)

---

#### **Prompt Used (`agents.py`)**

This module uses a highly specific prompt with a 0-9 rubric based on "knowledge depth". The agent is instructed to return only a JSON object.

```python
# This is the exact prompt from agents.py
"You are an evaluator of news articles.\n"
"Score each article from 0 to 9 based on knowledge depth:\n\n"
"0–2: Poor — highly superficial, incomplete, or factually questionable.\n"
"3–5: Moderate — covers basics but lacks depth or misses key points.\n"
"6–8: Good — detailed, covers multiple aspects, balanced and factual.\n"
"9: Exceptional — comprehensive, in-depth, authoritative, and well-structured.\n\n"
"Return valid JSON only in the format:\n"
"{\n"
'  "score": <integer 0–9>,\n'
'  "reason": "<short reason>"\n'
"}"
```

---

#### **How it Works (`article_scorer.py`)**

The main script `article_scorer.py` orchestrates the entire scoring process through several key steps:

---

##### **🔹 Step 1: Fetch & Group**

The script fetches all articles from MongoDB and groups them by title to de-duplicate the scoring process. This ensures that duplicate articles (same title, different sources) receive the same score, avoiding redundant API calls.

---

##### **🔹 Step 2: Get LLM Score**

For one representative article from each group, the script calls the `get_llm_score` function. This function is designed to be robust and resilient:

**Process:**
1. Attempts to get a score from the primary model (Gemini) via the `api_manager`
2. The agent analyzes the article content and returns a JSON with:
   - `score`: Integer from 0-9
   - `reason`: Short explanation

**API Failover Mechanism:**
- If the Gemini API fails due to rate limits (`ResourceExhausted`), the `api_manager` is instructed to `switch_to_groq()`
- The function automatically retries the request using the Groq model as a failover
- This ensures the scoring process continues even when one API is unavailable

---

##### **🔹 Step 3: Find User Score**

The script iterates through the grouped articles to find any existing `user_article_score` (e.g., from a user's manual rating or feedback).

**Purpose:** Incorporates user feedback into the final score when available.

---

##### **🔹 Step 4: Calculate Final Score**

The `final_custom_score` is a weighted average that combines AI analysis with user feedback.

**Formula Used (`article_scorer.py`):**

```python
# This is the exact formula from article_scorer.py
final_score = round((llm_score * 0.6) + (user_score * 0.4), 2) if user_score is not None else llm_score
```

**Scoring Logic:**
- **If user_score exists:** `final_score = (60% × llm_score) + (40% × user_score)`
- **If no user_score:** `final_score = llm_score`

This weighted approach ensures that AI analysis carries more weight (60%) while still incorporating valuable user feedback (40%) when available.

---

##### **🔹 Step 5: Update All & Save**

**Update MongoDB:**
- The `final_score` and its components (`llm_score`, `user_article_score`) are saved back to all articles in the group in MongoDB
- This ensures all duplicate articles receive the same score

**Save Local Copy:**
- All scores are also saved to a local `article_scores.json` file for logging and backup purposes

---

#### **Key Features**

- ✅ **Resilient API Handling:** Automatic failover from Gemini to Groq prevents scoring failures
- ✅ **Deduplication:** Groups articles by title to avoid redundant scoring
- ✅ **Hybrid Scoring:** Combines AI analysis (60%) with user feedback (40%)
- ✅ **Comprehensive Logging:** Saves scores both to MongoDB and local JSON file
- ✅ **Knowledge Depth Focus:** Uses a 0-9 rubric specifically designed to evaluate article depth and quality

---

### ✅ **Module 5: Recommendation Engine**

**Directory:** `backend/Recommendation_Engine/`  
**Purpose:** Matches users with most relevant articles using a sophisticated multi-stage pipeline that combines user behavior analysis, AI-powered profile generation, and vector similarity matching.

---

#### **The Recommendation Pipeline: Complete Flow**

The recommendation system follows a precise, multi-step process that transforms raw user interactions into personalized article recommendations.

---

##### **🔹 Trigger: User Interaction**

The pipeline begins when a user performs an action in the frontend:

- **Liking an article** (via `ArticleCard.tsx`)
- **Defining interests** in their profile (via `UserPreferences.tsx`)

These actions are logged in MongoDB, creating records of:
- `liked_article_ids` — List of articles the user has interacted with
- `explicit_preferences` — Raw text preferences (e.g., "I like AI and finance")

---

##### **🔹 Step 1: User Analysis (`user_analyzer.py`)**

When a recommendation is needed, this script creates a unified "profile" of the user's interests.

**Process:**
1. Fetches two data sources from MongoDB:
   - The user's `liked_article_ids`
   - The user's `explicit_preferences` (raw text)
2. Retrieves the full text content (or summaries) of all liked articles
3. Collects all preference data into a single dataset

**Output:** A collection of raw, "noisy" text data (e.g., 5 liked articles + 3 preference phrases)

---

##### **🔹 Step 2: The Analysis Agent (`agents.py`)**

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

##### **🔹 Step 3: Profile Vectorization (`embeddings.py`)**

The clean "interest paragraph" from Step 2 is converted into a mathematical representation.

**Process:**
1. The interest paragraph is fed into the embedding model (from `backend/Embedding_Creation/embeddings.py`)
2. Uses SentenceTransformer (`all-MiniLM-L6-v2`) to generate vector embeddings
3. Output: A single **User Profile Vector** (e.g., a `[1, 384]` array)

**Storage:** This vector is saved in the user's MongoDB document for quick retrieval, avoiding recomputation on every request.

---

##### **🔹 Step 4: The Final Recommendation (`article_recommender.py`)**

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

##### **🔹 Step 5: Ranking and Delivery**

The final step sorts and delivers the most relevant articles.

**Process:**
1. Sorts the `similarity_scores` array from highest to lowest
2. Takes the **Top 10** article IDs from this sorted list
3. Returns the final list as a JSON response to the frontend
4. Frontend displays these articles to the user in `News.tsx`

**Result:** Users receive personalized article recommendations that match their interests, behavior, and stated preferences.

---

#### **Key Files in Recommendation Engine**

- **`user_analyzer.py`** — Analyzes user behavior and preferences
- **`agents.py`** — Contains the User Analyzer Agent (LLM-based profile generation)
- **`article_recommender.py`** — Core matching engine using cosine similarity
- **`engine.py`** — Orchestrates the recommendation pipeline
- **`model_loader.py`** — Loads embedding models for vectorization

---

### ✅ **Module 6: WhatsApp Messaging**

**Directory:** `backend/Whatsapp_Messaging/`  
**Purpose:** Delivers personalized news recommendations to users via WhatsApp using Twilio API, with scheduled delivery based on user preferences.

**How it Works:**

1. **Scheduled Tasks (`scheduler_tasks.py`):**
   - Uses APScheduler to run periodic tasks
   - Fetches users with phone numbers and preferred delivery times
   - Triggers recommendation generation for each user

2. **Message Generation (`whatsapp_sender.py`):**
   - Retrieves top 10 recommended articles for each user
   - Formats articles into WhatsApp-friendly message format
   - Includes article titles, summaries, and links

3. **Sending (`whatsapp_service.py`):**
   - Uses Twilio API to send messages
   - Handles message formatting and delivery
   - Logs delivery status

4. **Integration:**
   - Connected to Recommendation Engine for article selection
   - Respects user's `preferred_time` setting
   - Sends daily/weekly digests based on user preferences

**Key Features:**
- ✅ **Scheduled Delivery:** CRON-based scheduling via APScheduler
- ✅ **Personalized Content:** Uses recommendation engine for article selection
- ✅ **Time Preferences:** Respects user's preferred delivery time
- ✅ **Twilio Integration:** Reliable message delivery via Twilio API

**Files:**
- `whatsapp_sender.py` — Main sending logic
- `whatsapp_service.py` — Twilio API integration
- `scheduler_tasks.py` — Scheduled task management
- `recommender.py` — Article recommendation integration

---

## 💾 **Database Schema & Format**

The NewsVerse platform uses MongoDB to store articles, user data, preferences, and recommendations. Below are the detailed schemas for each collection.

---

### ✅ **1. Article Collection**

The main collection storing all scraped and processed articles.

**Collection Name:** `articles` (or similar, as configured)

**Document Structure:**
```json
{
  "_id": "HT_20250908_141827_5388",
  "source": "HT",
  "title": "Vice-president election on Sept 9: Numbers back NDA as Radhakrishnan b…",
  "date": "2025-09-08",
  "time": "13:43:25",
  "content": "The stage is set for CP Radhakrishnan andSudershan Reddyto battle it o…",
  "url": "https://www.hindustantimes.com/india-news/vice-president-election-on-s…",
  "scraped_at": "2025-09-08T14:18:27.311+00:00",
  "summarization": {
    "summary": "Factual summary text...",
    "story_summary": "Child-friendly story format..."
  },
  "sentiment": "Neutral",
  "fact_check": {
    "llm_verdict": false,
    "fact_check_explanation": "The article claims that Jagdeep Dhankhar resigned as Vice President on…"
  },
  "article_score": {
    "user_article_score": 5,
    "llm_score": 6,
    "final_custom_score": 5.6
  },
  "embedding": [/* Array of 384 dimensions */],
  "rated_by": ["darshvaishnani1234@gmail.com"],
  "processed_status": {
    "summarized": true,
    "fact_checked": true,
    "sentiment": true,
    "ner": true,
    "scored": true
  }
}
```

**Key Fields:**
- **`_id`**: Unique identifier (format: `{SOURCE}_{DATE}_{TIME}_{RANDOM}`)
- **`source`**: News source abbreviation (e.g., "HT", "BBC", "CNN")
- **`embedding`**: Vector embedding (384 dimensions) for similarity matching
- **`article_score`**: Quality score from Article Scorer module
- **`rated_by`**: Array of user emails who have rated this article

---

### ✅ **2. User Collection**

Stores user profile information, preferences, and interaction history.

**Collection Name:** `users` (or similar, as configured)

**Document Structure:**
```json
{
  "_id": "68be98c16b193cc8e8317f73",
  "email": "darshvaishnani1234@gmail.com",
  "name": "Darsh Vaishnani",
  "picture": "https://lh3.googleusercontent.com/a/ACg8ocJ_ZBbPNqLG1JJikCsw90INemaPXd…",
  "phone_number": "+919375981112",
  "preferred_time": "01:38",
  "rated_articles": ["BBC_20250908_141827_6617"],
  "ner_data": {
    "Person": [
      "Rohit Arya",
      "Deepak Kesarkar",
      "Ashish Shelar",
      "Mohsin Naqvi",
      "Devajit Sakia",
      "Shukla",
      "Suryakumar Yadav",
      "Salman Agha"
    ],
    "Location": [/* Array of location entities */],
    "Organization": [/* Array of organization entities */]
  },
  "title_id_list": [
    "IndianExpress_20251031_230549_6828",
    "IndianExpress_20251001_004427_9329"
  ],
  "title_list": [
    "Behind the Powai tragedy: Rohit Arya's long fight with Maharashtra's S…",
    "BCCI ex-officio leaves ACC meeting midway in protest, says Mohsin Naqv…"
  ],
  "user_profile_vector": [/* Array of 384 dimensions - optional */],
  "explicit_preferences": [/* Array of user-stated interests - optional */]
}
```

**Key Fields:**
- **`rated_articles`**: Array of article IDs the user has rated/liked
- **`ner_data`**: Named entities extracted from user's liked articles
- **`title_id_list`**: IDs of articles the user has interacted with
- **`title_list`**: Titles of articles for quick reference
- **`user_profile_vector`**: Pre-computed embedding vector for recommendations (optional, cached)

---

### ✅ **3. UserPreferenceAnalysis Collection**

Stores the AI-generated detailed summary of user interests.

**Collection Name:** `user_preference_analysis` (or similar, as configured)

**Document Structure:**
```json
{
  "_id": {
    "$oid": "690516fce88e1f8c72949dee"
  },
  "email": "darshvaishnani1234@gmail.com",
  "name": "Darsh Vaishnani",
  "detailed_summary": "Based on the provided entities, the user seems to be interested in news related to education initiatives in India, particularly in Maharashtra (given mentions of 'School Education Department', 'Mazi Shala Sundar Shala', 'School Education Commissionerate', 'Powai', 'Pune', 'Mumbai'). They also seem interested in events and campaigns like 'Mahatma Gandhi Jayanti Se Sardar Patel Jayanti Tak', 'Vikasit Bharat Buildothon', 'Veer Gatha 5.0', 'Ek Ped Ma Ke Naam', and 'Mission Life Eco Club'. There's also a strong interest in cricket, with mentions of 'Suryakumar Yadav', 'Salman Agha', 'Board of Control for Cricket (BCCI)', 'Asian Cricket Council (ACC)', and 'Pakistan Cricket Board (PCB)', implying an interest in India-Pakistan cricket relations and tournaments possibly held in 'Dubai'. The user may also follow news from 'The Indian Express'.\n"
}
```

**Purpose:** This collection stores the output from Step 2 of the Recommendation Pipeline (The Analysis Agent). The `detailed_summary` is the distilled interest paragraph that gets vectorized for recommendations.

---

### ✅ **4. RecommendedArticle Collection**

Stores pre-computed article recommendations for each user.

**Collection Name:** `recommended_articles` (or similar, as configured)

**Document Structure:**
```json
{
  "_id": {
    "$oid": "690516ae8b1f3d3714c87f83"
  },
  "email": "darshvaishnani1234@gmail.com",
  "articles": [
    {
      "_id": "IndianExpress_20251031_230549_6828",
      "title": "Behind the Powai tragedy: Rohit Arya's long fight with Maharashtra's School Education Dept",
      "similarity": 0.2422
    },
    {
      "_id": "IndianExpress_20251001_004427_9329",
      "title": "BCCI ex-officio leaves ACC meeting midway in protest, says Mohsin Naqvi gave no clarity over Asia Cup trophy",
      "similarity": 0.2483
    }
    // ... up to 10 articles
  ]
}
```

**Key Fields:**
- **`email`**: User identifier
- **`articles`**: Array of top 10 recommended articles
  - **`_id`**: Article identifier
  - **`title`**: Article title for display
  - **`similarity`**: Cosine similarity score (0.0–1.0) indicating match quality

**Purpose:** This collection caches the results from Step 5 of the Recommendation Pipeline, allowing quick retrieval of personalized recommendations without recalculating similarity scores on every request.

---

## 🚀 **How to Run the Project**

### ✅ **Prerequisites**

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **MongoDB** (local or cloud instance)
- **API Keys** (stored in `.env` file):
  - Google OAuth credentials
  - OpenAI/Groq API keys
  - Gemini API key
  - Twilio credentials
  - MongoDB connection URI

---

### ✅ **Backend Setup**

```bash
# Navigate to backend directory
cd backend
```

#### **Create & Activate Virtual Environment**

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

#### **Install Dependencies**

```bash
pip install -r requirements.txt
```

#### **Configure Environment Variables**

Create a `.env` file in the `backend/` directory:

```env
# MongoDB
MONGO_URI=your_mongodb_connection_string

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key

# LLM APIs
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_phone

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

#### **Run FastAPI Server**

```bash
uvicorn main:app --reload
```

**Server runs at:**  
👉 http://localhost:8000

**API Documentation:**  
👉 http://localhost:8000/docs (Swagger UI)  
👉 http://localhost:8000/redoc (ReDoc)

---

### ✅ **Frontend Setup**

```bash
# Navigate to frontend directory
cd frontend
```

#### **Install Dependencies**

```bash
npm install
```

#### **Run Vite Dev Server**

```bash
npm run dev
```

**App runs at:**  
👉 http://localhost:5173

---

## 📖 **API Documentation**

### **Main FastAPI Server (`main.py`)**

The FastAPI server provides the following key endpoints:

#### **Authentication Endpoints**
- `GET /auth/google` - Initiate Google OAuth login
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/logout` - Logout user
- `GET /user` - Get current user information

#### **Article Endpoints**
- `GET /articles` - Get articles (with filtering/pagination)
- `GET /articles/{article_id}` - Get specific article
- `POST /articles/{article_id}/rate` - Rate an article

#### **Recommendation Endpoints**
- `GET /recommendations` - Get personalized recommendations for current user
- `POST /preferences` - Update user preferences

#### **Pipeline Endpoints** (Admin/Internal)
- `POST /pipeline/summarize` - Run summarization pipeline
- `POST /pipeline/fact-check` - Run fact-checking pipeline
- `POST /pipeline/sentiment` - Run sentiment analysis pipeline
- `POST /pipeline/score` - Run article scoring pipeline
- `POST /pipeline/preprocess` - Run full preprocessing pipeline

#### **WhatsApp Endpoints**
- `POST /whatsapp/send` - Send WhatsApp message (internal)

---

## 🔧 **Development Sandbox**

**Directory:** `Raw_code_developer/`

This directory contains:

- 🧪 **Early prototypes** - Initial proof-of-concept implementations
- 📓 **Notebook experiments** - Jupyter notebooks for testing
- 📚 **Crawl4ai tutorials** - Learning resources and examples
- 📊 **Sample datasets** - Example JSON files for testing
  - `BBC_filtered_news_articles.json`
  - `fact_check_results.json`
  - `sentiment_results.json`
  - `user_database.json`
- 💻 **Initial code** - Early versions of Summarization, Fact-Check, and Recommendation modules

---

## 📝 **License**

See [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using AI, React, and Python**

[Report Bug](https://github.com/your-repo/issues) • [Request Feature](https://github.com/your-repo/issues) • [Documentation](#-module-documentation)

</div>
