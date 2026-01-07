from fastapi import APIRouter, Depends, HTTPException
from app.models.portfolio import Portfolio
from app.api import dependencies
from sqlmodel import select, Session

router = APIRouter()

@router.get("/{job_id}")
async def get_portfolio_by_job(
    job_id: str, 
    db: Session = Depends(dependencies.get_db)
):

    statement = select(Portfolio).where(Portfolio.job_id == job_id)
    results = db.exec(statement)
    portfolio = results.first()

    if not portfolio:
        raise HTTPException(
            status_code=404, 
            detail="Portfolio not found. Might be in AI generation phase."
        )

    return portfolio