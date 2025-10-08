from sentence_transformers import SentenceTransformer
from Embedding_Creation import config

print(f"🧠 Loading embedding model: {config.EMBEDDING_MODEL}...")

# This line loads the model and stores it in the embedding_model variable.
# It will only run once when the module is first imported.
embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)

print("✅ Model loaded successfully.")