from dotenv import load_dotenv
import os

load_dotenv()

# FastAPI application configuration
PLATE_RECOGNIZER_API_URL = "https://api.platerecognizer.com/v1/plate-reader/"
API_KEY = os.getenv("PLATE_RECOGNIZER_API_KEY")
