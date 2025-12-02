"""Test service handlers for 46elks integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.exceptions import HomeAssistantError


@pytest.mark.asyncio
async def test_send_mms_without_capability(mock_hass, mock_elks_api):
    """Test sending MMS without MMS-capable number."""
    from custom_components.elks_46 import async_setup_entry
    from homeassistant.core import ServiceCall

    # Setup entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "api_username": "test_user",
        "api_password": "test_pass",
        "default_sender": "ELKS46",
    }

    # Mock numbers without MMS capability
    mock_elks_api.async_get_numbers = AsyncMock(return_value=[
        {"number": "+46766865802", "active": "yes", "capabilities": ["voice", "sms"]},
    ])

    with patch("custom_components.elks_46.ElksApi", return_value=mock_elks_api):
        await async_setup_entry(mock_hass, entry)

    # Try to send MMS
    call = MagicMock(spec=ServiceCall)
    call.data = {
        "from": "+46766865802",
        "to": "+46701234567",
        "message": "Test",
        "image": "https://example.com/image.jpg",
    }

    # Get the registered service handler
    service_handler = mock_hass.services.async_register.call_args_list[-1][0][2]

    with pytest.raises(HomeAssistantError, match="cannot send MMS"):
        await service_handler(call)


@pytest.mark.asyncio
async def test_make_call_without_voice_capability(mock_hass, mock_elks_api):
    """Test making call without voice-capable number."""
    from custom_components.elks_46 import async_setup_entry
    from homeassistant.core import ServiceCall

    # Setup entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "api_username": "test_user",
        "api_password": "test_pass",
        "default_sender": "ELKS46",
    }

    # Mock numbers without voice capability
    mock_elks_api.async_get_numbers = AsyncMock(return_value=[
        {"number": "+46766865802", "active": "yes", "capabilities": ["sms"]},
    ])

    with patch("custom_components.elks_46.ElksApi", return_value=mock_elks_api):
        await async_setup_entry(mock_hass, entry)

    # Try to make call
    call = MagicMock(spec=ServiceCall)
    call.data = {
        "from": "+46766865802",
        "to": "+46701234567",
        "audio_url": "https://example.com/audio.mp3",
    }

    # Get the registered service handler (make_call is second service)
    service_handler = mock_hass.services.async_register.call_args_list[1][0][2]

    with pytest.raises(HomeAssistantError, match="cannot make calls"):
        await service_handler(call)


@pytest.mark.asyncio
async def test_send_mms_with_capability(mock_hass, mock_elks_api):
    """Test sending MMS with MMS-capable number."""
    from custom_components.elks_46 import async_setup_entry
    from homeassistant.core import ServiceCall

    # Setup entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "api_username": "test_user",
        "api_password": "test_pass",
        "default_sender": "ELKS46",
    }

    # Mock numbers with MMS capability
    mock_elks_api.async_get_numbers = AsyncMock(return_value=[
        {"number": "+46701234567", "active": "yes", "capabilities": ["voice", "sms", "mms"]},
    ])

    with patch("custom_components.elks_46.ElksApi", return_value=mock_elks_api):
        await async_setup_entry(mock_hass, entry)

    # Send MMS
    call = MagicMock(spec=ServiceCall)
    call.data = {
        "from": "+46701234567",
        "to": "+46709876543",
        "message": "Test",
        "image": "https://example.com/image.jpg",
    }

    # Get the registered service handler (send_mms is third service)
    service_handler = mock_hass.services.async_register.call_args_list[-1][0][2]

    # Should not raise
    await service_handler(call)

    # Verify MMS was sent
    mock_elks_api.async_send_mms.assert_called_once_with(
        mock_hass,
        "+46701234567",
        "+46709876543",
        "Test",
        "https://example.com/image.jpg",
    )


@pytest.mark.asyncio
async def test_insufficient_balance(mock_hass, mock_elks_api):
    """Test service calls with insufficient balance."""
    from custom_components.elks_46 import async_setup_entry
    from homeassistant.core import ServiceCall

    # Setup entry
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "api_username": "test_user",
        "api_password": "test_pass",
        "default_sender": "ELKS46",
    }

    # Mock zero balance
    mock_elks_api.async_get_account_info = AsyncMock(return_value={
        "balance": 0,
    })

    with patch("custom_components.elks_46.ElksApi", return_value=mock_elks_api):
        await async_setup_entry(mock_hass, entry)

    # Try to send SMS with zero balance
    call = MagicMock(spec=ServiceCall)
    call.data = {
        "to": "+46701234567",
        "message": "Test",
    }

    # Get the registered service handler (send_sms is first service)
    service_handler = mock_hass.services.async_register.call_args_list[0][0][2]

    with pytest.raises(HomeAssistantError, match="Insufficient balance"):
        await service_handler(call)
