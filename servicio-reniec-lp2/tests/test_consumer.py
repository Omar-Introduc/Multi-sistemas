import json
from unittest.mock import MagicMock, patch
import pytest
from consumer import callback

@patch('consumer.SessionLocal')
def test_callback_success(mock_session):
    channel = MagicMock()
    method = MagicMock()
    properties = MagicMock()
    body = json.dumps({"dni": "12345678"}).encode()

    mock_db = MagicMock()
    mock_session.return_value = mock_db

    with patch("consumer.get_persona_by_dni") as mock_get_persona:
        mock_get_persona.return_value = {"dni": "12345678", "nombres": "Juan"}
        callback(channel, method, properties, body)
        mock_get_persona.assert_called_once_with(mock_db, "12345678")
        channel.basic_ack.assert_called_once()

@patch('consumer.SessionLocal')
def test_callback_invalid_dni(mock_session):
    channel = MagicMock()
    method = MagicMock()
    properties = MagicMock()
    body = json.dumps({"dni": "invalid"}).encode()

    mock_db = MagicMock()
    mock_session.return_value = mock_db

    with patch("consumer.get_persona_by_dni") as mock_get_persona:
        mock_get_persona.return_value = None
        callback(channel, method, properties, body)
        mock_get_persona.assert_called_once_with(mock_db, "invalid")
        channel.basic_ack.assert_called_once()

@patch('consumer.SessionLocal')
def test_callback_malformed_json(mock_session):
    channel = MagicMock()
    method = MagicMock()
    properties = MagicMock()
    body = b'{"dni": "12345678"'

    callback(channel, method, properties, body)
    channel.basic_nack.assert_called_once()
