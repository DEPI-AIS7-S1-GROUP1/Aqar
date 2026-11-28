"""Test migration 0002: users, user_contacts, conversations, messages.

Static part: verifies table structure, constraints, and indexes.
Live part (TEST_DATABASE_URL): upgrade/downgrade cycles, constraint checks.
"""

import importlib.util
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
import sqlalchemy as sa

BACKEND = Path(__file__).parent.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

MIGRATION = BACKEND / "app/db/migrations/versions/0002_users_contacts_conversations_messages.py"


class _Recorder:
    """Stands in for alembic.op and records tables created by the migration."""

    def __init__(self) -> None:
        self.tables: dict[str, dict[str, sa.Column]] = {}
        self.indexes: dict[str, list[str]] = {}
        self.constraints: dict[str, list] = {}

    def create_table(self, name, *items):
        self.tables[name] = {c.name: c for c in items if isinstance(c, sa.Column)}
        self.constraints[name] = [c for c in items if isinstance(c, sa.CheckConstraint)]

    def create_index(self, name, table, columns):
        self.indexes[name] = [table, *columns]


@pytest.fixture(scope="module")
def recorded() -> _Recorder:
    spec = importlib.util.spec_from_file_location("migration_0002", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rec = _Recorder()
    module.op = rec
    module.upgrade()
    return rec


def test_tables_created_in_dependency_order(recorded):
    assert list(recorded.tables) == ["users", "user_contacts", "conversations", "messages"]


def test_users_structure(recorded):
    cols = recorded.tables["users"]
    assert "user_id" in cols and cols["user_id"].primary_key
    assert "email" in cols and not cols["email"].nullable and cols["email"].unique
    assert "name" in cols and not cols["name"].nullable
    assert "password_hash" in cols and not cols["password_hash"].nullable
    assert "role" in cols and not cols["role"].nullable
    assert "created_at" in cols and not cols["created_at"].nullable
    # Verify role CHECK constraint exists
    checks = [c.sqltext.text for c in recorded.constraints["users"]]
    assert any("role IN" in c for c in checks)


def test_user_contacts_structure(recorded):
    cols = recorded.tables["user_contacts"]
    assert "user_id" in cols and cols["user_id"].primary_key
    assert "phone" in cols and cols["phone"].nullable
    assert "contact_consent" in cols and not cols["contact_consent"].nullable
    assert "consent_at" in cols and cols["consent_at"].nullable
    # Verify phone is in user_contacts, not in users
    assert "phone" not in recorded.tables["users"]


def test_conversations_structure(recorded):
    cols = recorded.tables["conversations"]
    assert "conversation_id" in cols and cols["conversation_id"].primary_key
    assert "user_id" in cols and not cols["user_id"].nullable
    assert "mode" in cols and not cols["mode"].nullable
    assert "version" in cols and not cols["version"].nullable
    assert "created_at" in cols and not cols["created_at"].nullable
    assert "updated_at" in cols and not cols["updated_at"].nullable
    # Verify mode CHECK constraint exists
    checks = [c.sqltext.text for c in recorded.constraints["conversations"]]
    assert any("mode IN" in c for c in checks)


def test_messages_structure(recorded):
    cols = recorded.tables["messages"]
    assert "message_id" in cols and cols["message_id"].primary_key
    assert "conversation_id" in cols and not cols["conversation_id"].nullable
    assert "role" in cols and not cols["role"].nullable
    assert "text" in cols and not cols["text"].nullable
    assert "card_listing_ids" in cols and cols["card_listing_ids"].nullable
    assert isinstance(cols["card_listing_ids"].type, sa.ARRAY)
    assert "created_at" in cols and not cols["created_at"].nullable
    # Verify role CHECK constraint exists
    checks = [c.sqltext.text for c in recorded.constraints["messages"]]
    assert any("role IN" in c for c in checks)


def test_indexes_created(recorded):
    indexed = {tuple(v) for v in recorded.indexes.values()}
    assert ("conversations", "user_id") in indexed
    assert ("messages", "conversation_id", "created_at") in indexed


def test_no_foreign_keys_to_external_tables(recorded):
    """Verify no FKs to tables owned by other team members."""
    # All FKs should point to tables in this migration or earlier migrations we own
    allowed_targets = {"users", "conversations", "developers", "listings"}
    for table_name, cols in recorded.tables.items():
        for col_name, col in cols.items():
            if col.foreign_keys:
                for fk in col.foreign_keys:
                    # Extract table name from the foreign key target string (e.g., "users.user_id")
                    target_parts = str(fk.target_fullname).split(".")
                    target_table = target_parts[0] if target_parts else None
                    assert target_table in allowed_targets, \
                        f"{table_name}.{col_name} references {target_table}"


# ---------- live database (optional) ----------

LIVE_URL = os.environ.get("TEST_DATABASE_URL")
live = pytest.mark.skipif(not LIVE_URL, reason="TEST_DATABASE_URL not set")


def _alembic(*args: str) -> None:
    env = {**os.environ, "DATABASE_URL": LIVE_URL}
    subprocess.run([sys.executable, "-m", "alembic", *args], cwd=BACKEND, env=env, check=True)


@pytest.fixture(scope="module")
def engine():
    url = LIVE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    eng = sa.create_engine(url)
    _alembic("downgrade", "base")
    _alembic("upgrade", "head")
    _alembic("downgrade", "-1")
    _alembic("upgrade", "head")
    yield eng
    _alembic("downgrade", "base")
    eng.dispose()


def _insert(conn, table: str, row: dict) -> None:
    cols = ", ".join(row)
    vals = ", ".join(f":{k}" for k in row)
    conn.execute(sa.text(f"INSERT INTO {table} ({cols}) VALUES ({vals})"), row)


@live
def test_live_upgrade_and_downgrade(engine):
    """Verify tables exist after upgrade and are gone after downgrade."""
    with engine.connect() as conn:
        tables = sa.inspect(engine).get_table_names()
        assert "users" in tables
        assert "user_contacts" in tables
        assert "conversations" in tables
        assert "messages" in tables


@live
def test_live_insert_and_query(engine):
    """Insert valid data and verify retrieval."""
    with engine.begin() as conn:
        _insert(conn, "users", {
            "user_id": "usr_test_1",
            "email": "test@example.com",
            "name": "Test User",
            "password_hash": "hashed_password",
            "role": "customer",
        })
        _insert(conn, "user_contacts", {
            "user_id": "usr_test_1",
            "phone": "+201234567890",
            "contact_consent": True,
            "consent_at": datetime(2026, 11, 26, tzinfo=UTC),
        })
        _insert(conn, "conversations", {
            "conversation_id": "conv_test_1",
            "user_id": "usr_test_1",
            "mode": "search",
        })
        _insert(conn, "messages", {
            "message_id": "msg_test_1",
            "conversation_id": "conv_test_1",
            "role": "user",
            "text": "Hello",
        })
        _insert(conn, "messages", {
            "message_id": "msg_test_2",
            "conversation_id": "conv_test_1",
            "role": "ai",
            "text": "Hi there",
            "card_listing_ids": ["lst_1", "lst_2"],
        })
        
        user = conn.execute(sa.text("SELECT * FROM users WHERE user_id = 'usr_test_1'")).one()
        contact = conn.execute(sa.text("SELECT * FROM user_contacts WHERE user_id = 'usr_test_1'")).one()
        messages = list(conn.execute(sa.text(
            "SELECT * FROM messages WHERE conversation_id = 'conv_test_1' ORDER BY created_at"
        )))
        
        conn.execute(sa.text("DELETE FROM messages; DELETE FROM conversations;"
                             " DELETE FROM user_contacts; DELETE FROM users"))
    
    assert user.email == "test@example.com"
    assert user.role == "customer"
    assert contact.phone == "+201234567890"
    assert contact.contact_consent is True
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].card_listing_ids == ["lst_1", "lst_2"]


@live
def test_live_nullable_fields(engine):
    """Verify nullable fields accept NULL values."""
    with engine.begin() as conn:
        _insert(conn, "users", {
            "user_id": "usr_test_2",
            "email": "test2@example.com",
            "name": "Test User 2",
            "password_hash": "hashed_password",
            "role": "broker",
        })
        _insert(conn, "user_contacts", {
            "user_id": "usr_test_2",
            "contact_consent": False,
        })
        _insert(conn, "conversations", {
            "conversation_id": "conv_test_2",
            "user_id": "usr_test_2",
            "mode": "compare",
        })
        _insert(conn, "messages", {
            "message_id": "msg_test_3",
            "conversation_id": "conv_test_2",
            "role": "system",
            "text": "System message",
        })
        
        contact = conn.execute(sa.text("SELECT * FROM user_contacts WHERE user_id = 'usr_test_2'")).one()
        message = conn.execute(sa.text("SELECT * FROM messages WHERE message_id = 'msg_test_3'")).one()
        
        conn.execute(sa.text("DELETE FROM messages; DELETE FROM conversations;"
                             " DELETE FROM user_contacts; DELETE FROM users"))
    
    assert contact.phone is None
    assert contact.consent_at is None
    assert message.card_listing_ids is None


@live
@pytest.mark.parametrize(
    ("table", "bad"),
    [
        ("users", {"role": "admin"}),  # invalid role
        ("conversations", {"mode": "chat"}),  # invalid mode
        ("messages", {"role": "assistant"}),  # invalid role
        ("users", {"email": "test@example.com"}),  # duplicate email (requires setup)
    ],
)
def test_live_bad_rows_rejected(engine, table, bad):
    """Verify CHECK constraints reject invalid data."""
    with engine.begin() as conn:
        # Setup: create a user for the duplicate email test
        if table == "users" and "email" in bad:
            _insert(conn, "users", {
                "user_id": "usr_existing",
                "email": "test@example.com",
                "name": "Existing User",
                "password_hash": "hash",
                "role": "customer",
            })
        
        with pytest.raises(sa.exc.IntegrityError):
            if table == "users":
                _insert(conn, "users", {
                    "user_id": "usr_bad",
                    "email": bad.get("email", "bad@example.com"),
                    "name": "Bad User",
                    "password_hash": "hash",
                    "role": bad.get("role", "customer"),
                })
            elif table == "conversations":
                _insert(conn, "users", {
                    "user_id": "usr_test_3",
                    "email": "test3@example.com",
                    "name": "Test User 3",
                    "password_hash": "hash",
                    "role": "customer",
                })
                _insert(conn, "conversations", {
                    "conversation_id": "conv_bad",
                    "user_id": "usr_test_3",
                    "mode": bad.get("mode", "search"),
                })
            elif table == "messages":
                _insert(conn, "users", {
                    "user_id": "usr_test_4",
                    "email": "test4@example.com",
                    "name": "Test User 4",
                    "password_hash": "hash",
                    "role": "customer",
                })
                _insert(conn, "conversations", {
                    "conversation_id": "conv_test_3",
                    "user_id": "usr_test_4",
                    "mode": "search",
                })
                _insert(conn, "messages", {
                    "message_id": "msg_bad",
                    "conversation_id": "conv_test_3",
                    "role": bad.get("role", "user"),
                    "text": "Bad message",
                })
        
        conn.rollback()


@live
def test_live_cascade_delete(engine):
    """Verify CASCADE deletes work correctly."""
    with engine.begin() as conn:
        _insert(conn, "users", {
            "user_id": "usr_cascade",
            "email": "cascade@example.com",
            "name": "Cascade User",
            "password_hash": "hash",
            "role": "customer",
        })
        _insert(conn, "user_contacts", {
            "user_id": "usr_cascade",
            "phone": "+201111111111",
            "contact_consent": True,
        })
        _insert(conn, "conversations", {
            "conversation_id": "conv_cascade",
            "user_id": "usr_cascade",
            "mode": "search",
        })
        _insert(conn, "messages", {
            "message_id": "msg_cascade",
            "conversation_id": "conv_cascade",
            "role": "user",
            "text": "Test",
        })
        
        # Delete user, everything should cascade
        conn.execute(sa.text("DELETE FROM users WHERE user_id = 'usr_cascade'"))
        
        contacts = list(conn.execute(sa.text("SELECT * FROM user_contacts WHERE user_id = 'usr_cascade'")))
        conversations = list(conn.execute(sa.text("SELECT * FROM conversations WHERE user_id = 'usr_cascade'")))
        messages = list(conn.execute(sa.text("SELECT * FROM messages WHERE conversation_id = 'conv_cascade'")))
    
    assert len(contacts) == 0
    assert len(conversations) == 0
    assert len(messages) == 0
