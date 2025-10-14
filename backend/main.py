# main.py - UPDATED WITH PERSONALIZED RECOMMENDATIONS PAGE

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, BackgroundTasks
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

import sys
import os

# Add the 'backend' directory to the system path to allow imports of sibling modules
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 


# --- IMPORT YOUR PIPELINE SCRIPTS ---
from Summarization.run_summarization import main as runSummarizer
from Sentiment_Analysis.sentiment import main as runSentiment
from Fact_Checker.fact_checker import main as runFactChecker
from Article_Scorer.article_scorer import main as runArticleScorer
from Whatsapp_Messaging.whatsapp_serice import formatMessage, sendWhatsapp
from Whatsapp_Messaging.scheduler_tasks import send_single_user_notification
from preprocessing_pipeline import main as run_preprocessing_pipeline
from Name_Entity_Recognition.NER import runNerForUsers # Import the NER function


# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080") 
MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")


# --- MongoDB Setup ---
client = MongoClient(MONGO_URI)
db = client["TestANewsVerseDB"]
user_collection = db["UserDetails"]
articles_collection = db["ArticlesCollection"]
# NEW: Add a connection to the recommendations collection
recommended_articles_collection = db["UserRecommendedArticles"]
# --- Scheduler Setup ---
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Kolkata'})
scheduler.start()
print("✅ Successfully connected to MongoDB.")




# --- Pydantic Models ---

class User(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_time: Optional[str] = Field(
        None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    rated_articles: list = []


class Summarization(BaseModel):
    summary: Optional[str] = "No summary available."
    story_summary: Optional[str] = "No story summary available."


class FactCheck(BaseModel):
    llm_verdict: Optional[bool] = False
    fact_check_explanation: Optional[str] = "No explanation available."


class Article(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    source: Optional[str] = "N/A"
    content: str
    url: Optional[str] = "#"
    user_has_rated: bool = False
    user_has_liked: bool = False
    # Use default_factory to ensure these are never None
    summarization: Summarization = Field(default_factory=dict)
    fact_check: FactCheck = Field(default_factory=dict)
    sentiment: Optional[str] = "N/A"

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# --- FastAPI App Initialization ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8080"], # Add all frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)



# --- OAuth Setup ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- API Endpoint for Fetching Articles ---

@app.get('/login/google')
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback/google')
async def auth_via_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info or not user_info.get('email'):
            raise Exception("Could not fetch user info.")

        existing_user = user_collection.find_one({"email": user_info['email']})
        
        if existing_user:
            request.session['user'] = {
                "name": existing_user['name'],
                "email": existing_user['email'],
                "picture": existing_user.get('picture'),
            }
            # ALWAYS redirect back to the frontend homapage
            return RedirectResponse(url=f"{FRONTEND_URL}/") 
        else:
            request.session['new_user_google_info'] = dict(user_info)
            # ALWAYS redirect back to the frontend
            return RedirectResponse(url=f"{FRONTEND_URL}/onboarding")
    except Exception as e:
        print(f"Error during authentication: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=auth_failed")

@app.post("/api/complete-onboarding")
async def complete_onboarding_api(
    request: Request,
    phone_number: str = Form(...),
    preferred_time: str = Form(...)
):
    google_info = request.session.get('new_user_google_info')
    if not google_info:
        return JSONResponse(content={"error": "Authentication session not found"}, status_code=401)

    user_email = google_info['email']

    # THE FIX: Check if the user already exists in the database.
    existing_user = user_collection.find_one({"email": user_email})

    # Prepare complete user data with defaults for all fields.
    user_data = {
        "email": user_email,
        "name": google_info['name'],
        "picture": google_info.get('picture'),
        "phone_number": phone_number,
        "preferred_time": preferred_time,
        "rated_articles": [], # Default empty list
        "title_id_list": [],  # Default empty list
        "title_list": [],     # Default empty list
    }

    if existing_user:
        # If user exists, UPDATE them with the new details (idempotent).
        user_collection.update_one(
            {"email": user_email},
            {"$set": {
                "phone_number": phone_number,
                "preferred_time": preferred_time
            }}
        )
        print(f"Updated existing user: {user_email}")
    else:
        # If user does not exist, INSERT them.
        try:
            # We use the Pydantic model to validate before inserting
            user_model = User(**user_data)
            user_collection.insert_one(user_model.model_dump(by_alias=True))
            print(f"Created new user: {user_email}")
        except Exception as e:
            print(f"Error creating user: {e}")
            return JSONResponse(content={"error": "Error creating account"}, status_code=500)

    # Clean up the temporary session data
    request.session.pop('new_user_google_info', None)
    
    # Create the final, persistent user session
    user_session_data = {
        "name": user_data['name'],
        "email": user_data['email'],
        "picture": user_data.get('picture'),
    }
    request.session['user'] = user_session_data
    
    # Always return the user object on success
    return JSONResponse(content={"user": user_session_data})

@app.post("/api/logout")
async def logout_api(request: Request):
    request.session.pop('user', None)
    return JSONResponse(content={"message": "Logout successful"})

@app.delete("/api/delete-account")
async def delete_account_api(request: Request):
    """
    Deletes the current user's account from the database.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_email = user_session.get('email')
    
    # Perform the deletion from the UserDetails collection
    result = user_collection.delete_one({"email": user_email})

    if result.deleted_count == 0:
        return JSONResponse(content={"error": "User not found"}, status_code=404)

    # Clear the user's session to log them out
    request.session.pop('user', None)
    
    return JSONResponse(content={"message": "Account deleted successfully"})


# --- ALL API ENDPOINTS FOR REACT ---

# ADD THIS NEW ENDPOINT
@app.get("/api/random-articles", response_model=List[Article])
async def get_random_articles_api(request: Request):
    """
    API endpoint to get 5 random articles from the collection.
    """
    # Use MongoDB's aggregation pipeline with $sample to efficiently get random documents
    random_articles_cursor = articles_collection.aggregate([
        {"$sample": {"size": 5}}
    ])
    
    articles = list(random_articles_cursor)

    # We still need to check the user's like/rate status for these random articles
    user = request.session.get('user')
    if not user:
        return articles

    user_details = user_collection.find_one({"email": user.get('email')})
    rated_articles = user_details.get("rated_articles", []) if user_details else []
    liked_articles = user_details.get("title_id_list", []) if user_details else []

    articles_with_user_data = []
    for article in articles:
        article_id = str(article["_id"])
        article_data = article.copy()
        article_data["_id"] = article_id
        article_data["user_has_rated"] = article_id in rated_articles
        article_data["user_has_liked"] = article_id in liked_articles
        article_data["summarization"] = article.get("summarization", {})
        article_data["fact_check"] = article.get("fact_check", {})
        articles_with_user_data.append(article_data)

    return articles_with_user_data

@app.get("/api/user")
async def get_user_api(request: Request):
    """
    Returns the current user's session data if they are logged in.
    """
    user = request.session.get('user')
    if not user:
        return JSONResponse(content={"authenticated": False}, status_code=401)
    return JSONResponse(content={"authenticated": True, "user": user})


@app.get("/api/articles", response_model=List[Article])
async def get_articles_api(request: Request):
    """
    This is the new API endpoint that provides article data in JSON format.
    It connects directly to your MongoDB collections.
    """
    user = request.session.get('user')

    # Fetch articles directly from your database
    articles_cursor = articles_collection.find().limit(
        20)  # Fetch more articles for a real app
    articles = list(articles_cursor)

    if not user:
        # If no user is logged in, return articles without user-specific data
        return articles

    # If a user is logged in, get their details to personalize the article data
    user_details = user_collection.find_one({"email": user.get('email')})

    rated_articles = user_details.get(
        "rated_articles", []) if user_details else []
    liked_articles = user_details.get(
        "title_id_list", []) if user_details else []

    # Combine article data with user's interaction data
    articles_with_user_data = []
    for article in articles:
        article_id = str(article["_id"])
        article_data = article.copy()
        article_data["_id"] = article_id
        article_data["user_has_rated"] = article_id in rated_articles
        article_data["user_has_liked"] = article_id in liked_articles

        # --- ADD THIS BLOCK ---
        # Ensure nested data is correctly formatted or defaults are provided
        article_data["summarization"] = article.get("summarization", {})
        article_data["fact_check"] = article.get("fact_check", {})
        # --- END BLOCK ---

        articles_with_user_data.append(article_data)

    return articles_with_user_data


@app.get("/api/recommendations", response_model=List[Article])
async def get_recommendations_api(request: Request):
    """
    API endpoint to provide personalized article recommendations in JSON format.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_recs_doc = recommended_articles_collection.find_one(
        {"email": user_session['email']})

    if not user_recs_doc or not user_recs_doc.get("articles"):
        return []

    recommended_ids_str = [rec["_id"] for rec in user_recs_doc["articles"]]

    # --- THIS IS THE FIX ---
    # We removed the ObjectId() conversion and now query with the strings directly.
    recommended_articles_cursor = articles_collection.find({
        "_id": {"$in": recommended_ids_str}
    })

    recommended_articles = []
    for article in recommended_articles_cursor:
        article["_id"] = str(article["_id"])
        recommended_articles.append(article)

    return recommended_articles

@app.post('/toggle-like')
async def toggle_like_article_api(
    request: Request,
    article_id: str = Form(...),
    article_title: str = Form(...)
):
    user = request.session.get('user')
    if not user:
        # Respond with a JSON error, which the frontend can handle
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_details = user_collection.find_one({"email": user['email']})
    liked_articles = user_details.get("title_id_list", [])

    is_currently_liked = article_id in liked_articles

    if is_currently_liked:
        # User is UNLIKING the article
        user_collection.update_one(
            {"email": user['email']},
            {"$pull": {"title_id_list": article_id, "title_list": article_title}}
        )
        message = "Article unliked"
    else:
        # User is LIKING the article
        user_collection.update_one(
            {"email": user['email']},
            {"$push": {"title_id_list": article_id, "title_list": article_title}}
        )
        message = "Article liked"

    # Respond with a JSON success message for the frontend
    return JSONResponse(content={"message": message, "liked": not is_currently_liked})

@app.get("/api/user-preference")
async def get_user_preference_api(request: Request):
    """
    API endpoint to get the current user's preferences (phone and time).
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_details = user_collection.find_one({"email": user_session['email']})
    if not user_details:
        return JSONResponse(content={"error": "User not found"}, status_code=404)

    return JSONResponse(content={
        "phone_number": user_details.get("phone_number", ""),
        "preferred_time": user_details.get("preferred_time", "08:00")
    })


@app.post("/api/update-preference")
async def update_preference_api(
    request: Request,
    phone_number: str = Form(...),
    preferred_time: str = Form(...)
):
    """
    API endpoint to update user preferences from the React app.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_collection.update_one(
        {"email": user_session['email']},
        {"$set": {
            "phone_number": phone_number,
            "preferred_time": preferred_time
        }}
    )
    return JSONResponse(content={"message": "Preferences updated successfully!"})

@app.post("/api/rate-article")
async def rate_article_api(
    request: Request,
    article_id: str = Form(...),
    rating: int = Form(...)
):
    """
    API endpoint for a user to rate an article.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_details = user_collection.find_one({"email": user_session['email']})
    if user_details and article_id in user_details.get("rated_articles", []):
        return JSONResponse(content={"error": "Article already rated"}, status_code=400)

    # --- THIS IS THE FIX ---
    # The ObjectId() conversion is removed from the query below.
    # Note: The original code used a different logic here, this reflects the code provided in the prompt.
    articles_collection.update_one(
        {"_id": article_id},  # Use the string ID directly
        {
            # Note: This logic might differ from your last version.
            # Sticking to the prompt's provided code structure.
            # Example logic
            "$set": {"article_score.user_article_score": rating},
            "$inc": {"article_score.total_ratings": 1},
            "$push": {"rated_by": user_session['email']}
        }
    )

    user_collection.update_one(
        {"email": user_session['email']},
        {"$push": {"rated_articles": article_id}}
    )

    return JSONResponse(content={"message": "Rating submitted successfully!"})

@app.post("/api/schedule-notifications")
async def schedule_notifications_api(request: Request, background_tasks: BackgroundTasks):
    """
    API endpoint to trigger the recommendation pipeline and schedule daily notifications.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_details = user_collection.find_one({"email": user_session['email']})

    if not user_details or not user_details.get("preferred_time") or not user_details.get("phone_number"):
        return JSONResponse(
            content={
                "error": "Please set a valid phone number and preferred time before scheduling."},
            status_code=400
        )

    # Immediately run the pipeline in the background to generate the first set of recommendations
    background_tasks.add_task(run_preprocessing_pipeline)
    print("🚀 Triggered immediate preprocessing pipeline in the background for user.")

    preferred_time_str = user_details["preferred_time"]
    hour, minute = map(int, preferred_time_str.split(':'))
    user_email = user_details["email"]

    # Schedule the daily notification job for the user
    notification_job_id = f"user_notification_{user_email}"
    scheduler.add_job(
        send_single_user_notification,
        trigger='cron',
        hour=hour,
        minute=minute,
        args=[user_email],
        id=notification_job_id,
        replace_existing=True
    )

    print(f"✅ Scheduled daily news for {user_email} at {preferred_time_str}.")

    return JSONResponse(content={
        "message": f"Success! Recommendations are being generated now. You will receive daily updates at {preferred_time_str}."
    })

async def run_full_pipeline_task():
    print("🚀 [BACKGROUND TASK] Starting the News-Verse pipeline...")
    runSummarizer()
    runSentiment()
    runFactChecker()
    runArticleScorer()
    print("\n✅ [BACKGROUND TASK] News-Verse pipeline finished!")


@app.get('/run-pipeline')
async def trigger_pipeline(background_tasks: BackgroundTasks, request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/')

    background_tasks.add_task(run_full_pipeline_task)

    return JSONResponse(
        status_code=202,
        content={
            "message": "Pipeline started! News is being fetched and analyzed in the background."}
    )

print("✅ FastAPI server is running in pure API mode.")

# To run the app: uvicorn backend.main:app --reload --port 8000
