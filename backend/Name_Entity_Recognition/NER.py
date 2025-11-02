# In Newsverse-main/backend/Name_Entity_Recognition/NER.py

import logging

# --- FIX 1: Set up the logger directly ---
logger = logging.getLogger("NERPipeline")
logger.setLevel(logging.INFO)
# --- (End of logging setup) ---


# --- Import the correct function from your agents.py ---
from Name_Entity_Recognition.agents import get_ner_agent 

from Name_Entity_Recognition.db_manager import connectToDbs, fetchAllUsers, fetchArticleById, updateUserNer

# --- FIX 2: Only import parseJsonOutput ---
from Name_Entity_Recognition.utils import parseJsonOutput


def runNerForUsers():
    """Main function to run NER processing for all users."""
    try:
        # --- Get the agent from your function ---
        logger.info("=" * 60)
        logger.info("Starting NER processing pipeline...")
        logger.info("=" * 60)
        
        logger.info("Step 1: Initializing NER agent...")
        ner_agent = get_ner_agent()
        
        if ner_agent is None:
            logger.error("❌ Failed to initialize NERAgent from get_ner_agent(). Aborting NER process.")
            return False

        logger.info("✅ NER agent initialized successfully")

        logger.info("Step 2: Connecting to MongoDB databases...")
        news_collection, user_collection = connectToDbs()

        if news_collection is None or user_collection is None:
            logger.error("❌ Failed to connect to one or more DB collections. Aborting NER.")
            return False

        logger.info("✅ Database connections established")

        logger.info("Step 3: Fetching all users from database...")
        users = fetchAllUsers(user_collection)
        logger.info(f"✅ Found {len(users)} users to process for NER.")

        if len(users) == 0:
            logger.warning("⚠️ No users found in database. Nothing to process.")
            return False

        # Diagnostic: Check how many articles exist in the database
        try:
            total_articles = news_collection.count_documents({})
            logger.info(f"📊 Database contains {total_articles} total articles")
            # Sample some article IDs to see the format
            sample_articles = list(news_collection.find({}, {"_id": 1}).limit(5))
            if sample_articles:
                sample_ids = [str(doc["_id"]) for doc in sample_articles]
                logger.debug(f"   Sample article IDs: {sample_ids}")
        except Exception as e:
            logger.debug(f"   Could not get article statistics: {e}")

        successful_users = 0
        failed_users = 0

        for idx, user in enumerate(users, 1):
            user_name = user.get('name', 'N/A')
            user_email = user.get('email', 'N/A')
            logger.info("=" * 60)
            logger.info(f"Processing user {idx}/{len(users)}: '{user_name}' ({user_email})...")
            
            try:
                user_mongo_id = user['_id']
                title_id_list = user.get('title_id_list', [])

                aggregated_entities = {
                    "Person": [],
                    "Location": [],
                    "Organization": []
                }

                if not title_id_list:
                    logger.warning(f"⚠️ User '{user_name}' has no liked articles (title_id_list is empty). Skipping.")
                    failed_users += 1
                    continue

                logger.info(f"   Found {len(title_id_list)} articles to process for user '{user_name}'")
                logger.debug(f"   Article IDs: {title_id_list[:5]}{'...' if len(title_id_list) > 5 else ''}")
                
                # Check how many of these articles actually exist
                existing_count = 0
                for aid in title_id_list[:10]:  # Check first 10 as sample
                    clean_aid = aid.strip() if isinstance(aid, str) else str(aid).strip()
                    if clean_aid and news_collection.find_one({"_id": clean_aid}):
                        existing_count += 1
                if existing_count < len(title_id_list[:10]) and len(title_id_list) > 0:
                    logger.warning(f"   ⚠️ Only {existing_count}/{min(10, len(title_id_list))} sample articles exist in database. "
                                 f"Some article IDs in user's title_id_list may be stale/deleted.")

                processed_articles = 0
                skipped_articles = 0
                error_articles = 0

                for article_idx, article_id in enumerate(title_id_list, 1):
                    clean_article_id = article_id.strip() if isinstance(article_id, str) else str(article_id).strip()
                    if not clean_article_id:
                        skipped_articles += 1
                        continue

                    logger.info(f"   Processing article {article_idx}/{len(title_id_list)}: {clean_article_id}")

                    article = fetchArticleById(news_collection, clean_article_id)

                    if not article:
                        logger.warning(f"   ⚠️ Article '{clean_article_id}' not found in database. Skipping.")
                        skipped_articles += 1
                        continue
                        
                    if 'content' not in article or not article['content']:
                        logger.warning(f"   ⚠️ Article {clean_article_id} has no content. Skipping.")
                        skipped_articles += 1
                        continue

                    try:
                        # ner_agent.run() returns a RunOutput object, not a string
                        logger.debug(f"   Running NER agent on article {clean_article_id}...")
                        response = ner_agent.run(article['content'])
                        
                        # Extract the 'content' attribute from the RunOutput object
                        if hasattr(response, 'content'):
                            response_string = response.content
                        else:
                            response_string = str(response)
                        
                        if not response_string:
                            logger.warning(f"   ⚠️ Agent returned empty response for article {clean_article_id}")
                            error_articles += 1
                            continue
                        
                        # parseJsonOutput turns the string into a dict
                        entities_dict = parseJsonOutput(response_string)
                        
                        if not entities_dict:
                            logger.warning(f"   ⚠️ Could not parse JSON from agent for article {clean_article_id}")
                            logger.debug(f"   Raw response: {response_string[:200] if isinstance(response_string, str) else str(response_string)[:200]}...")
                            error_articles += 1
                            continue

                        # Loop through the types (Person, Location, Organization)
                        for entity_type in aggregated_entities.keys():
                            # Get the list of words for this type (e.g., ["Google", "Microsoft"])
                            words = entities_dict.get(entity_type, [])
                            
                            # Add only unique words to our main list
                            for word in words:
                                if word and isinstance(word, str) and word.strip() and word not in aggregated_entities[entity_type]:
                                    aggregated_entities[entity_type].append(word.strip())
                        
                        processed_articles += 1
                            
                    except Exception as e:
                        logger.error(f"   ❌ Error processing NER for article {clean_article_id}: {e}", exc_info=True)
                        error_articles += 1
                        continue # Skip this article if AI agent fails

                logger.info(f"   Processed: {processed_articles}, Skipped: {skipped_articles}, Errors: {error_articles}")
                logger.info(f"   Extracted entities - Person: {len(aggregated_entities['Person'])}, "
                          f"Location: {len(aggregated_entities['Location'])}, "
                          f"Organization: {len(aggregated_entities['Organization'])}")

                # Save the single, aggregated dictionary to the user's document
                logger.info(f"   Saving NER data to database for user '{user_name}'...")
                update_success = updateUserNer(user_collection, user_mongo_id, aggregated_entities)
                
                if update_success:
                    logger.info(f"   ✅ Successfully updated NER for user '{user_name}'")
                    successful_users += 1
                else:
                    logger.error(f"   ❌ Failed to update NER data for user '{user_name}'")
                    failed_users += 1
                    
            except KeyError as e:
                logger.error(f"   ❌ Missing required field in user document: {e}", exc_info=True)
                failed_users += 1
            except Exception as e:
                logger.error(f"   ❌ Unexpected error processing user '{user_name}': {e}", exc_info=True)
                failed_users += 1

        logger.info("=" * 60)
        logger.info(f"NER processing complete!")
        logger.info(f"   Successfully processed: {successful_users} users")
        logger.info(f"   Failed: {failed_users} users")
        logger.info(f"   Total: {len(users)} users")
        logger.info("=" * 60)
        
        return successful_users > 0
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR in runNerForUsers: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    runNerForUsers()