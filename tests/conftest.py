"""Common fixtures for 46elks tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_elks_api():
    """Mock ElksApi client."""
    with patch("custom_components.elks_46.ElksApi") as mock:
        api = MagicMock()

        # Mock account info
        api.async_get_account_info = AsyncMock(return_value={
            "id": "u123456",
            "displayname": "Test User",
            "balance": 1974000,  # 197.40 SEK in öre
        })

        # Mock numbers with different capabilities
        api.async_get_numbers = AsyncMock(return_value=[
            {
                "id": "n123",
                "number": "+46766865802",
                "active": "yes",
                "capabilities": ["voice", "sms"],
            },
            {
                "id": "n124",
                "number": "+46701234567",
                "active": "yes",
                "capabilities": ["voice", "sms", "mms"],
            },
        ])

        # Mock capability filters
        api.get_mms_capable_numbers = lambda numbers: [
            num.get("number") for num in numbers
            if num.get("active") == "yes" and "mms" in num.get("capabilities", [])
        ]

        # Mock SMS history
        api.async_get_sms_history = AsyncMock(return_value=[
            {
                "id": "s123",
                "from": "ELKS46",
                "to": "+46701234567",
                "message": "Test message",
                "direction": "outgoing",
                "created": "2025-12-02T10:30:00",
                "cost": 350,
            }
        ])

        # Mock call history
        api.async_get_call_history = AsyncMock(return_value=[
            {
                "id": "c123",
                "from": "+46766865802",
                "to": "+46701234567",
                "direction": "outgoing",
                "created": "2025-12-02T11:00:00",
                "cost": 1200,
                "duration": 45,
            }
        ])

        # Mock send methods
        api.async_send_sms = AsyncMock(return_value={"id": "s124", "status": "created"})
        api.async_make_call = AsyncMock(return_value={"id": "c124", "status": "ongoing"})
        api.async_send_mms = AsyncMock(return_value={"id": "m123", "status": "created"})

        mock.return_value = api
        yield api


@pytest.fixture
def mock_hass():
    """Mock HomeAssistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func: func())

    # Mock config_entries
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

    # Mock services
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()

    return hass
