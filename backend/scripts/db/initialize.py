from __future__ import annotations

from alembic import command, config

from db.base_db import BaseDB
from db.db_session_manager import DBSessionManager
from models.listing.db import ListingDB
from models.market.db import MarketDB
from models.property.db import PropertyDB
from utils.filesystem import get_module_root


def initialize_database():
    """Initializes database, including creating tables and setting latest alembic revision"""
    engine = DBSessionManager.create_psql_engine()
    BaseDB.metadata.create_all(engine)

    alembic_ini = get_module_root(__file__) / "alembic.ini"
    alembic_config = config.Config(alembic_ini)

    command.stamp(alembic_config, "head")


if __name__ == "__main__":
    initialize_database()
