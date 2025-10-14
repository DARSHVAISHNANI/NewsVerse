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
import logging 
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
from Name_Entity_Recognition.NER import runNerForUsers


# Load environment variables from .env file
load_dotenv()

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("NewsverseBackend")


# --- Configuration ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080") 
MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")


# --- MongoDB Setup ---
try:
    client = MongoClient(MONGO_URI)
    db = client["TestANewsVerseDB"]
    user_collection = db["UserDetails"]
    articles_collection = db["ArticlesCollection"]
    recommended_articles_collection = db["UserRecommendedArticles"]
    logger.info("Successfully connected to MongoDB.")
except Exception as e:
    logger.critical(f"FATAL: Could not connect to MongoDB. Check MONGO_URI. Error: {e}")


# --- Scheduler Setup ---
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Kolkata'})
scheduler.start()


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
    allow_origins=[FRONTEND_URL, "http://localhost:8080"],
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
    logger.info("Initiating Google login redirect.")
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
            logger.info(f"Existing user logged in: {user_info['email']}")
            return RedirectResponse(url=f"{FRONTEND_URL}/") 
        else:
            request.session['new_user_google_info'] = dict(user_info)
            logger.info(f"New user redirected to onboarding: {user_info['email']}")
            return RedirectResponse(url=f"{FRONTEND_URL}/onboarding")
    except Exception as e:
        logger.error(f"Error during authentication: {e}", exc_info=True)
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=auth_failed")

@app.post("/api/complete-onboarding")
async def complete_onboarding_api(
    request: Request,
    phone_number: str = Form(...),
    preferred_time: str = Form(...)
):
    google_info = request.session.get('new_user_google_info')
    if not google_info:
        logger.warning("Attempted onboarding without an active Google session.")
        return JSONResponse(content={"error": "Authentication session not found"}, status_code=401)

    user_email = google_info['email']

    try:
        existing_user = user_collection.find_one({"email": user_email})

        user_data = {
            "email": user_email,
            "name": google_info['name'],
            "picture": google_info.get('picture'),
            "phone_number": phone_number,
            "preferred_time": preferred_time,
            "rated_articles": [],
            "title_id_list": [],
            "title_list": [],
        }

        if existing_user:
            user_collection.update_one(
                {"email": user_email},
                {"$set": {
                    "phone_number": phone_number,
                    "preferred_time": preferred_time
                }}
            )
            logger.info(f"Updated existing user: {user_email}")
        else:
            user_model = User(**user_data)
            user_collection.insert_one(user_model.model_dump(by_alias=True))
            logger.info(f"Created new user: {user_email}")
            
    except Exception as e:
        logger.error(f"Error creating user {user_email}: {e}", exc_info=True)
        return JSONResponse(content={"error": "Error creating account"}, status_code=500)

    request.session.pop('new_user_google_info', None)
    
    user_session_data = {
        "name": user_data['name'],
        "email": user_data['email'],
        "picture": user_data.get('picture'),
    }
    request.session['user'] = user_session_data
    
    return JSONResponse(content={"user": user_session_data})

@app.post("/api/logout")
async def logout_api(request: Request):
    user_session = request.session.get('user')
    if user_session:
        logger.info(f"User logged out: {user_session.get('email')}")
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
    
    try:
        result = user_collection.delete_one({"email": user_email})

        if result.deleted_count == 0:
            logger.warning(f"Attempted to delete non-existent account: {user_email}")
            return JSONResponse(content={"error": "User not found"}, status_code=404)

        # Clear the user's session to log them out
        request.session.pop('user', None)
        logger.info(f"Account deleted successfully: {user_email}")
        return JSONResponse(content={"message": "Account deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting account for {user_email}: {e}", exc_info=True)
        return JSONResponse(content={"error": "Server error during deletion"}, status_code=500)


# --- ALL API ENDPOINTS FOR REACT ---

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
        20)
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
        article_data["summarization"] = article.get("summarization", {})
        article_data["fact_check"] = article.get("fact_check", {})
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

    user_email = user_session['email']
    
    try:
        user_details = user_collection.find_one({"email": user_email})
        if user_details and article_id in user_details.get("rated_articles", []):
            logger.warning(f"User {user_email} attempted to re-rate article {article_id}.")
            return JSONResponse(content={"error": "Article already rated"}, status_code=400)

        articles_collection.update_one(
            {"_id": ObjectId(article_id)}, 
            {
                "$set": {"article_score.user_article_score": rating},
                "$inc": {"article_score.total_ratings": 1},
                "$push": {"rated_by": user_email}
            }
        )

        user_collection.update_one(
            {"email": user_email},
            {"$push": {"rated_articles": article_id}}
        )
        logger.info(f"User {user_email} rated article {article_id} with score {rating}.")

        return JSONResponse(content={"message": "Rating submitted successfully!"})

    except Exception as e:
        logger.error(f"Database error submitting rating for article {article_id} by {user_email}: {e}", exc_info=True)
        return JSONResponse(content={"error": "Server error submitting rating"}, status_code=500)

@app.post("/api/schedule-notifications")
async def schedule_notifications_api(request: Request, background_tasks: BackgroundTasks):
    """
    API endpoint to trigger the recommendation pipeline and schedule daily notifications.
    """
    user_session = request.session.get('user')
    if not user_session:
        return JSONResponse(content={"error": "Not authenticated"}, status_code=401)

    user_email = user_session['email']
    user_details = user_collection.find_one({"email": user_email})

    if not user_details or not user_details.get("preferred_time") or not user_details.get("phone_number"):
        logger.warning(f"Scheduling failed for {user_email}: missing time or phone.")
        return JSONResponse(
            content={
                "error": "Please set a valid phone number and preferred time before scheduling."},
            status_code=400
        )

    # Immediately run the pipeline in the background to generate the first set of recommendations
    background_tasks.add_task(run_preprocessing_pipeline)
    logger.info("Triggered immediate preprocessing pipeline in the background for user.")

    preferred_time_str = user_details["preferred_time"]
    hour, minute = map(int, preferred_time_str.split(':'))
    
    try:
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
        logger.info(f"Scheduled daily news for {user_email} at {preferred_time_str}.")
    except Exception as e:
        logger.error(f"Error scheduling job for {user_email}: {e}", exc_info=True)
        return JSONResponse(content={"error": "Server error scheduling updates"}, status_code=500)


    return JSONResponse(content={
        "message": f"Success! Recommendations are being generated now. You will receive daily updates at {preferred_time_str}."
    })


async def run_full_pipeline_task():
    try:
        logger.info("[BACKGROUND TASK] Starting the News-Verse pipeline...")
        runSummarizer()
        runSentiment()
        runFactChecker()
        runArticleScorer()
        logger.info("[BACKGROUND TASK] News-Verse pipeline finished!")
    except Exception as e:
        logger.error(f"[BACKGROUND TASK] Error running full pipeline: {e}", exc_info=True)


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

logger.info("FastAPI server is running in pure API mode.")