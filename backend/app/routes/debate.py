"""Debate routing endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix='/debate', tags=['Debate'])

@router.get('/')
def get_debate_status():
    """Get current debate status."""
    return {'status': 'pending'}
