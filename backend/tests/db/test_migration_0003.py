import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"), reason="needs DATABASE_URL (use a Neon branch)"
)

NEW_COLUMNS = {"title", "unit_type", "bedrooms", "image_urls", "image_credit"}


def listing_columns(engine):
    return {c["name"] for c in inspect(engine).get_columns("listings")}


def test_upgrade_then_downgrade():
    config = Config("alembic.ini")
    engine = create_engine(os.environ["DATABASE_URL"])

    command.upgrade(config, "0003")
    assert NEW_COLUMNS <= listing_columns(engine)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT data_version FROM data_meta")).scalar() == 0

    command.downgrade(config, "0001")
    assert not (NEW_COLUMNS & listing_columns(engine))
    assert "data_meta" not in inspect(engine).get_table_names()

    command.upgrade(config, "0003")  # leave the database upgraded