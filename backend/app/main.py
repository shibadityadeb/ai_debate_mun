"""FastAPI app entrypoint for Diplomatrix AI."""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Config
from app.routes.debate import router as debate_router

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

app = FastAPI(title='Diplomatrix AI')
config = Config.from_env()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_origin_regex=config.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Routes
app.include_router(debate_router, prefix='/api')

@app.get('/')
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'app': 'Diplomatrix AI'}
