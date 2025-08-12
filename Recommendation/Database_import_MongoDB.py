import json
from pymongo import MongoClient

def upload_to_mongodb(json_file_path, connection_string, db_name, collection_name):
    """
    Connects to a MongoDB Atlas cluster and uploads data from a JSON file.

    Args:
        json_file_path (str): The path to the JSON file.
        connection_string (str): The connection string for the MongoDB Atlas cluster.
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.
    """
    try:
        # Create a new client and connect to the server
        client = MongoClient(connection_string)

        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

        # Get the database and collection
        db = client[db_name]
        collection = db[collection_name]

        # Open and load the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Insert the data into the collection
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

        print(f"Successfully inserted data from {json_file_path} into the '{collection_name}' collection in the '{db_name}' database.")

    except Exception as e:
        print(e)
    finally:
        # Ensures that the client will close when you finish/error
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == '__main__':
    # --- PLEASE REPLACE THESE VALUES WITH YOURS ---
    JSON_FILE = r'C:\Users\darsh\Downloads\user_database.json'
    # Replace the uri string with your MongoDB deployment's connection string.
    CONN_STRING = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
    DB_NAME = "UserDB"
    COLLECTION_NAME = "UserCo"
    # ----------------------------------------------

    upload_to_mongodb(JSON_FILE, CONN_STRING, DB_NAME, COLLECTION_NAME)