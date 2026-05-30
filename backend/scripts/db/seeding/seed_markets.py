#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import delete, literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from rich import inspect as ri

from db.base_db import BaseDB
from db.db_session_manager import DBSessionManager
from models.market.db import MarketDB
from utils.filesystem import get_module_root


def insert_or_update(db_session: Session, DBModel: type[BaseDB], col_values: dict):
    insert_stmt = insert(DBModel.__table__).values(**col_values)
    full_stmt = insert_stmt.on_conflict_do_update(
        constraint=DBModel.__table__.primary_key,
        set_={
            **col_values,
            "updated_at": datetime.now(timezone.utc),  # force formatting
        },
    )
    db_session.execute(full_stmt)


def seed_db_with_markets():
    local_db_session = DBSessionManager().scoped_session()

    seed_data_dir = (
        get_module_root(__file__) / "scripts" / "db" / "seeding" / "seed_data"
    )

    for json_summary in seed_data_dir.glob("*.json"):
        with open(json_summary, "r") as f:
            try:
                market_data = json.load(f)
                ri(market_data, sort=True)
                market_details = market_data.get("market")

                market_dict = dict(
                    adr_usd=market_data.get("average_daily_rate", 0),
                    annual_revenue_usd=market_data.get("revenue", 0),
                    city=market_details.get("locality"),
                    country=market_details.get("country"),
                    listing_count=market_data.get("active_listings_count"),
                    last_updated=market_data.get(
                        "last_updated", datetime.now(timezone.utc)
                    ),
                    neighborhood=market_details.get("district", None),
                    occupancy_rate=market_data.get("occupancy"),
                    peak_months=market_data.get("peak_months", None),
                    region=market_details.get("region"),
                )

                insert_or_update(
                    db_session=local_db_session,
                    DBModel=MarketDB,
                    col_values=market_dict,
                )
                local_db_session.commit()
            except Exception as e:
                ri(e)
                local_db_session.rollback()


if __name__ == "__main__":
    seed_db_with_markets()
