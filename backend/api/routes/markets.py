from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from api.dependencies.db_session import DBSessionDependency
from api.models.market import MarketsListResponse
from db.db_session_manager import DBSessionManager
from models.market.facade import MarketFacade
from utils.logging.init import init_logging

logger = init_logging(__file__)

markets_router = APIRouter(prefix="/api")


@markets_router.get(
    "/markets",
    response_model=MarketsListResponse,
)
def read_markets_list(
    # db_session: DBSessionDependency
):
    markets = []

    try:
        db_session = DBSessionManager().scoped_session()

        markets = MarketFacade(db_session=db_session).get_all()
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")

    return {"data": markets}
