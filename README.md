# NewsVerse Backend

Welcome to the backend documentation for NewsVerse, a sophisticated news aggregation, analysis, and recommendation platform. This system is built as a series of interconnected microservices, leveraging AI agents to process, analyze, and deliver personalized news content.

## Backend Tech Stack

The backend is built primarily on a modern Python stack:

* **Programming Language:** Python 3.10+
* **API Framework:** FastAPI (inferred from `main.py` and `api_manager.py`)
* **Database:** MongoDB (inferred from multiple `db_manager.py` files and developer code)
* **AI Agent Framework:** An agent-based framework, likely using a library like **LangChain**, **AutoGen**, or a custom implementation (inferred from the multiple `agents.py` files).
* **Embedding Model:** A sentence-transformer model (like `all-MiniLM-L6-v2`) for generating vector embeddings (inferred from `backend/Embedding_Creation/`).
* **Messaging:** Twilio API for WhatsApp (inferred from `backend/Whatsapp_Messaging/`).
* **Core Libraries:** `pymongo`, `uvicorn`, `scikit-learn` (for similarity metrics), `python-dotenv`.

## Architecture Overview

The backend operates as a processing pipeline orchestrated by `main.py` and `api_manager.py`. Raw articles are ingested and then passed sequentially through a series of analysis modules. The results are stored in MongoDB, where they are used by the recommendation engine to serve personalized content to users via the frontend API or WhatsApp.



Here is a detailed breakdown of each component.

---

## 1. Scraping & Crawling

* **Directory:** `backend/Scraping_Crawling/`
* **Purpose:** This module is the entry point for all data. It is responsible for fetching raw article data (links, titles, body text) from various news sources.
* **Key Files:**
    * `scraper.py`: Contains the core logic for visiting target websites and extracting URLs.
    * `parsers.py`: Contains specific parsing logic for different website HTML structures.
    * `db_manager.py`: Handles writing the raw, unprocessed articles into the database.
* **Agents Used:** 0. This component appears to be a traditional web scraper (e.g., using `BeautifulSoup` or `Scrapy`) and does not use an LLM agent.

## 2. Article Processing Pipeline

Once articles are scraped, they are processed by a series of independent AI-driven modules. Each module reads an unprocessed article from the database, performs its task, and updates the article's document in MongoDB with new analytical data.

### A. Summarization

* **Directory:** `backend/Summarization/`
* **Purpose:** Generates a concise summary of the article body.
* **Agents Used:** 1 (The Summarization Agent).
* **Prompt Used:** The prompt logic is located in `agents.py`. It instructs the LLM to read a large text and distill its key points.
    * **Example Prompt Template (replace with your actual prompt):**
        ```python
        prompt = f"""
        You are a professional news editor. Summarize the following news article into 3 key bullet points, followed by a concise 80-word paragraph.
        
        Article:
        {article_text}
        
        Summary:
        """
        ```

### B. Fact-Checker

* **Directory:** `backend/Fact_Checker/`
* **Purpose:** Assesses the factual veracity of the claims made in the article.
* **Agents Used:** 1 (The Fact-Checking Agent).
* **Prompt Used:** The prompt in `agents.py` is designed to make the LLM cross-verify information and provide a "veracity score." This agent may also use a search tool (not visible in filenames) to check claims against external sources.
    * **Example Prompt Template (replace with your actual prompt):**
        ```python
        prompt = f"""
        Analyze the following article for factual accuracy. Identify the main claims.
        Return a JSON object with two keys:
        1. "veracity_score": A score from 0.0 to 1.0, where 1.0 is completely factual.
        2. "explanation": A brief explanation for your score, noting any unverified claims.
        
        Article:
        {article_text}
        
        Analysis:
        """
        ```

### C. Sentiment Analysis

* **Directory:** `backend/Sentiment_Analysis/`
* **Purpose:** Determines the overall emotional tone of the article.
* **Agents Used:** 1 (The Sentiment Analysis Agent).
* **Prompt Used:** The prompt in `agents.py` instructs the LLM to classify the text into a predefined category.
    * **Example Prompt Template (replace with your actual prompt):**
        ```python
        prompt = f"""
        Classify the sentiment of the following news article.
        Respond with only a single word: "Positive", "Negative", or "Neutral".
        
        Article:
        {article_text}
        
        Sentiment:
        """
        ```

### D. Name Entity Recognition (NER)

* **Directory:** `backend/Name_Entity_Recognition/`
* **Purpose:** Extracts key entities (people, organizations, locations) from the text. This is crucial for matching articles to user interests.
* **Agents Used:** 1 (The NER Agent).
* **Prompt Used:** The prompt in `agents.py` directs the LLM to act as an NER model and output structured data.
    * **Example Prompt Template (replace with your actual prompt):**
        ```python
        prompt = f"""
        Extract all named entities from the following text.
        Return a JSON object with three lists as keys: "people", "organizations", and "locations".
        If no entities are found for a category, return an empty list.
        
        Article:
        {article_text}
        
        Entities:
        """
        ```

## 3. Embedding Creation

* **Directory:** `backend/Embedding_Creation/`
* **Purpose:** This is a core ML module. It converts text data (both processed articles and user preferences) into numerical vector embeddings. These vectors allow for mathematical comparison of semantic similarity.
* **Key Files:**
    * `model_loader.py`: Loads the pre-trained embedding model (e.g., from SentenceTransformers).
    * `embeddings.py`: Contains the function to take text and return a vector.
    * `db_manager.py`: Updates database documents with their corresponding vector.
* **Agents Used:** 0. This is a traditional ML model, not an LLM agent.
* **Formula Used:** This module uses the loaded model (e.g., `all-MiniLM-L6-v2`) to perform a feed-forward pass, generating a vector (e.g., of 384 dimensions) for a given text.

## 4. Article Scorer

* **Directory:** `backend/Article_Scorer/`
* **Purpose:** Assigns a "quality" or "relevance" score to each article based on the combined outputs of the processing pipeline.
* **Agents Used:** 1 (The Scoring Agent).
* **Prompt Used:** The prompt in `agents.py` takes multiple data points (e.g., sentiment, fact-check score, timeliness) and asks the LLM to generate a single, holistic score.
    * **Example Prompt Template (replace with your actual prompt):**
        ```python
        prompt = f"""
        Based on the following analysis, score this article's overall quality from 1 (low) to 10 (high).
        
        Analysis:
        - Fact-Check Score: {fact_check_score}
        - Sentiment: {sentiment}
        - NER Entities: {list_of_entities}
        
        Your score must be a single integer.
        
        Score:
        """
        ```
* **Formula Used:** The agent itself may be one part of the score. A final formula in `article_scorer.py` likely combines the agent's score with other metrics.
    * **Example Formula (replace with your actual formula):**
        ```python
        # w1, w2, w3 are weights you define
        llm_score = agent_output 
        final_score = (w1 * llm_score) + (w2 * fact_check_score) + (w3 * (1.0 - recency_decay))
        ```

## 5. Recommendation Engine

* **Directory:** `backend/Recommendation_Engine/`
* **Purpose:** This is the brain of the application. It matches users with relevant articles.
* **Key Files:**
    * `user_analyzer.py`: Analyzes a user's preferences and reading history to generate a "user profile vector." This might involve averaging the vectors of articles they liked.
    * `article_recommender.py` / `engine.py`: The core logic that fetches the user vector and compares it against all article vectors in the database.
* **Agents Used:** 1 (The User Analyzer Agent in `agents.py`). This agent might be used to convert a user's unstructured text preferences (e.g., "I like tech and finance") into a structured query or keyword list for the `user_analyzer.py`.
* **Formula Used:** The core of the recommendation engine is **Cosine Similarity**. This formula measures the angle between the "user profile vector" and an "article vector." A smaller angle means higher similarity.
    * **Core Formula (in `article_recommender.py`):**
        ```python
        from sklearn.metrics.pairwise import cosine_similarity
        
        # user_vector is a [1, 384] shape array
        # article_vectors is a [N, 384] shape array (where N is num of articles)
        
        similarity_scores = cosine_similarity(user_vector, article_vectors)
        
        # Get the indices of the top-k highest scores
        top_k_indices = similarity_scores[0].argsort()[-k:][::-1]
        ```

## 6. WhatsApp Messaging

* **Directory:** `backend/Whatsapp_Messaging/`
* **Purpose:** Delivers the personalized news (generated by the Recommendation Engine) to users via WhatsApp.
* **Key Files:**
    * `whatsapp_sender.py`: Contains the logic to connect to the Twilio API and send a message.
    * `recommender.py`: A local module that likely calls the main `Recommendation_Engine` to get a list of articles for a specific user.
    * `scheduler_tasks.py`: Sets up a scheduled job (e.g., a CRON job) to run the recommendation and sending process automatically (e.g., every morning at 8 AM).
* **Agents Used:** 0. This is a utility and delivery module.
