import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "vectorstore")
