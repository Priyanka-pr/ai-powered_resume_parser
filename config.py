import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    LOCALHOST = os.getenv("LOCALHOST")
    REMOTEHOST = os.getenv("REMOTEHOST")
    MODEL = os.getenv("MODEL")

# OPENAI_API_KEY=""
# HUGGINGFACEHUB_API_TOKEN = ""

def set_environment():
    """Set environment variables for API-related configurations."""
    variable_dict = Config.__dict__.items()
    for key, value in variable_dict:
        if key.isupper(): 
            os.environ[key] = value

set_environment()
