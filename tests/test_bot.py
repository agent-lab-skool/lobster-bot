from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from core.bot import (
    handle_message,
    handle_new,
    handle_facts,
    handle_today,
    handle_usage,
    handle_help,
    is_authorized,
)
from core.bridge import ClaudeResponse


@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user.id = 111
    update.effective_chat.id = 111
    update.message.text = "Hello bot"
    update.message.reply_text = AsyncMock()
    update.message.chat.send_action = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    ctx = MagicMock()
    ctx.bot.send_message = AsyncMock()
    ctx.bot.send_chat_action = AsyncMock()
    return ctx


def test_is_authorized_allowed():
    assert is_authorized(111, [111, 222]) is True


def test_is_authorized_denied():
    assert is_authorized(999, [111, 222]) is False


@pytest.mark.asyncio
async def test_handle_message_unauthorized(mock_update, mock_context):
    mock_update.effective_user.id = 999
    with patch("core.bot._config", {"telegram": {"allowed_users": [111]}}):
        await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "not authorized" in mock_update.message.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_message_enqueues(mock_update, mock_context):
    mock_router = MagicMock()
    mock_router.enqueue = AsyncMock()

    with (
        patch("core.bot._config", {"telegram": {"allowed_users": [111]}}),
        patch("core.bot._router", mock_router),
    ):
        await handle_message(mock_update, mock_context)

    mock_router.enqueue.assert_called_once()
    call_args = mock_router.enqueue.call_args
    assert call_args[0][0] == 111  # chat_id
    assert call_args[0][1] == "Hello bot"  # message text


@pytest.mark.asyncio
async def test_handle_new_clears_session(mock_update, mock_context):
    with (
        patch("core.bot._config", {"telegram": {"allowed_users": [111]}}),
        patch("core.bot._sessions") as mock_sm,
    ):
        await handle_new(mock_update, mock_context)

    mock_sm.clear_session.assert_called_once_with(111)
    mock_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_handle_facts_shows_content(mock_update, mock_context, tmp_path):
    facts = tmp_path / "memory" / "facts.md"
    facts.parent.mkdir(parents=True)
    facts.write_text("Name: Alice\nTimezone: EST")

    with (
        patch("core.bot._config", {"telegram": {"allowed_users": [111]}}),
        patch("core.bot._project_dir", str(tmp_path)),
    ):
        await handle_facts(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with("Name: Alice\nTimezone: EST")


@pytest.mark.asyncio
async def test_handle_today_no_log(mock_update, mock_context, tmp_path):
    with (
        patch("core.bot._config", {"telegram": {"allowed_users": [111]}}),
        patch("core.bot._project_dir", str(tmp_path)),
    ):
        await handle_today(mock_update, mock_context)

    assert "no log" in mock_update.message.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_usage(mock_update, mock_context):
    mock_sessions = MagicMock()
    mock_sessions.get_usage.return_value = {
        "today": {"cost_usd": 0.0123, "input_tokens": 5000, "output_tokens": 2000, "messages": 10},
        "total": {"cost_usd": 0.4567, "input_tokens": 150000, "output_tokens": 60000, "messages": 200},
    }

    with (
        patch("core.bot._config", {"telegram": {"allowed_users": [111]}}),
        patch("core.bot._sessions", mock_sessions),
    ):
        await handle_usage(mock_update, mock_context)

    msg = mock_update.message.reply_text.call_args[0][0]
    assert "$0.0123" in msg
    assert "$0.4567" in msg
    assert "10 messages" in msg
    assert "200 messages" in msg


@pytest.mark.asyncio
async def test_handle_help(mock_update, mock_context):
    await handle_help(mock_update, mock_context)
    msg = mock_update.message.reply_text.call_args[0][0]
    assert "/new" in msg
    assert "/usage" in msg
    assert "/facts" in msg
    assert "/today" in msg
