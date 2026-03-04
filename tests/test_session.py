import time
from pathlib import Path

import pytest

from core.session import SessionManager


@pytest.fixture
def sm(tmp_path):
    return SessionManager(tmp_path / "sessions.db")


def test_no_session_initially(sm):
    assert sm.get_session(12345) is None


def test_store_and_retrieve_session(sm):
    sm.set_session(12345, "sess-abc")
    assert sm.get_session(12345) == "sess-abc"


def test_update_session(sm):
    sm.set_session(12345, "sess-old")
    sm.set_session(12345, "sess-new")
    assert sm.get_session(12345) == "sess-new"


def test_clear_session(sm):
    sm.set_session(12345, "sess-abc")
    sm.clear_session(12345)
    assert sm.get_session(12345) is None


def test_archive_stale_sessions(sm):
    sm.set_session(12345, "sess-abc")
    # Manually backdate the updated_at to simulate staleness
    sm._db.execute(
        "UPDATE sessions SET updated_at = updated_at - 90000 WHERE chat_id = ?",
        (12345,),
    )
    sm._db.commit()
    archived = sm.archive_stale(max_age_seconds=86400)
    assert archived == 1
    assert sm.get_session(12345) is None


def test_list_archived_sessions(sm):
    sm.set_session(12345, "sess-abc")
    sm._db.execute(
        "UPDATE sessions SET updated_at = updated_at - 90000 WHERE chat_id = ?",
        (12345,),
    )
    sm._db.commit()
    sm.archive_stale(max_age_seconds=86400)
    history = sm.get_history(12345)
    assert len(history) == 1
    assert history[0]["session_id"] == "sess-abc"


def test_log_and_get_usage(sm):
    sm.log_usage(111, cost_usd=0.005, input_tokens=100, output_tokens=50)
    sm.log_usage(111, cost_usd=0.003, input_tokens=80, output_tokens=30)

    usage = sm.get_usage()
    assert usage["today"]["cost_usd"] == pytest.approx(0.008)
    assert usage["today"]["input_tokens"] == 180
    assert usage["today"]["output_tokens"] == 80
    assert usage["today"]["messages"] == 2
    assert usage["total"]["messages"] == 2


def test_get_usage_empty(sm):
    usage = sm.get_usage()
    assert usage["today"]["cost_usd"] == 0
    assert usage["today"]["messages"] == 0
    assert usage["total"]["messages"] == 0


def test_get_usage_by_chat(sm):
    sm.log_usage(111, cost_usd=0.005, input_tokens=100, output_tokens=50)
    sm.log_usage(222, cost_usd=0.010, input_tokens=200, output_tokens=100)

    usage_111 = sm.get_usage(chat_id=111)
    assert usage_111["today"]["cost_usd"] == pytest.approx(0.005)
    assert usage_111["today"]["messages"] == 1

    usage_all = sm.get_usage()
    assert usage_all["today"]["cost_usd"] == pytest.approx(0.015)
    assert usage_all["today"]["messages"] == 2
