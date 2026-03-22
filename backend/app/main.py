"""FastAPI app entrypoint for Diplomatrix AI."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.debate import router as debate_router

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

app = FastAPI(title='Diplomatrix AI')

# CORS middleware
default_origins = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://ai-debate-mun.vercel.app',
    'https://diplomatrix-ai.vercel.app',
]
configured_origins = os.getenv('CORS_ALLOW_ORIGINS')
allow_origins = [
    origin.strip()
    for origin in (configured_origins.split(',') if configured_origins else default_origins)
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r'https://.*\.vercel\.app',
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
