from pymongo import MongoClient
import certifi
from sentence_transformers import SentenceTransformer
import numpy as np

client = MongoClient("mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/", tlsCAFile=certifi.where())
news_col = client["NewsVerseDB"]["NewsVerseCo"]

model = SentenceTransformer("all-MiniLM-L6-v2")

def store_article_embeddings():
    for article in news_col.find({"embedding": {"$exists": False}}):
        text = f"{article['title']} {article['body']}"
        embedding = model.encode(text).tolist()
        news_col.update_one({"_id": article["_id"]}, {"$set": {"embedding": embedding}})
    print("✅ Embeddings stored for all articles.")

if __name__ == "__main__":
    store_article_embeddings()