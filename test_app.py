# test_app.py
import pytest
from unittest.mock import patch, MagicMock
from app import generate_index_html, decode_data_uri, _do_pipeline, WORK_DIR
from pathlib import Path
import time

# -------------------
# Test generate_index_html
# -------------------


def test_index_html_content():
    html = generate_index_html(
        "Task1",
        "Brief for testing",
        attachments=[
            {"name": "sample.txt", "url": "data:text/plain;base64,SGVsbG8gd29ybGQ="}
        ],
    )
    assert '<h1 id="task-title">Task1</h1>' in html
    assert "Brief for testing" in html
    assert "attachment fallback" in html


def test_index_html_with_url_param():
    html = generate_index_html(
        "Task2", "Another brief", attachments=[], url="https://example.com/file.png"
    )
    assert '<h1 id="task-title">Task2</h1>' in html
    assert "Another brief" in html


def test_attachment_fallback_and_decoding():
    # Attachment without base64
    html = generate_index_html(
        "Task3",
        "Brief",
        attachments=[{"name": "file.txt", "url": "data:text/plain,plain_text"}],
    )
    data = decode_data_uri("data:text/plain,plain_text")
    assert data == b"plain_text"


# -------------------
# Test API pipeline (_do_pipeline)
# -------------------


@patch("app.notify_evaluation")
@patch("app.enable_pages")
@patch("app.git_init_commit_push")
@patch("app.create_repo_worktree")
def test_do_pipeline(mock_create, mock_git, mock_pages, mock_notify):
    # Setup mocks
    mock_create.return_value = (WORK_DIR / "dummy", "repo-name")
    mock_git.return_value = "commitsha123"
    mock_pages.return_value = None
    mock_notify.return_value = True

    data = {
        "email": "a@b.com",
        "task": "Task1",
        "brief": "Some brief",
        "round": 1,
        "nonce": "n1",
        "evaluation_url": "http://eval",
        "attachments": [],
    }

    _do_pipeline(data)

    mock_create.assert_called_once()
    mock_git.assert_called_once()
    mock_pages.assert_called_once()
    mock_notify.assert_called_once()
    # Check notify_evaluation payload
    args, kwargs = mock_notify.call_args
    assert args[0] == "http://eval"
    payload = args[1]
    assert payload["email"] == "a@b.com"
    assert payload["task"] == "Task1"
    assert payload["round"] == 1
    assert payload["commit_sha"] == "commitsha123"


# -------------------
# Test decode_data_uri
# -------------------


def test_decode_data_uri_base64():
    encoded = "data:text/plain;base64,SGVsbG8gd29ybGQ="
    result = decode_data_uri(encoded)
    assert result == b"Hello world"


def test_decode_data_uri_plain():
    plain = "data:text/plain,plain_text"
    result = decode_data_uri(plain)
    assert result == b"plain_text"
