"""FastAPI app entrypoint for Diplomatrix AI."""
from fastapi import FastAPI

app = FastAPI(title='Diplomatrix AI')

@app.get('/')
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'app': 'Diplomatrix AI'}
