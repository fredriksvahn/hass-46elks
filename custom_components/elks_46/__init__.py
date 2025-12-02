"""The 46elks integration."""
import json
import logging
from datetime import timedelta

import requests
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    API_BASE_URL,
    API_TIMEOUT,
    CONF_API_PASSWORD,
    CONF_API_USERNAME,
    CONF_DEFAULT_SENDER,
    DOMAIN,
    SERVICE_MAKE_CALL,
    SERVICE_SEND_MMS,
    SERVICE_SEND_SMS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Optional("from"): cv.string,
        vol.Required("to"): cv.string,
        vol.Required("message"): cv.string,
    }
)

MAKE_CALL_SCHEMA = vol.Schema(
    {
        vol.Required("from"): cv.string,
        vol.Required("to"): cv.string,
        vol.Required("audio_url"): cv.string,
    }
)

SEND_MMS_SCHEMA = vol.Schema(
    {
        vol.Required("from"): cv.string,
        vol.Required("to"): cv.string,
        vol.Optional("message"): cv.string,
        vol.Optional("image"): cv.string,
    }
)


class ElksApi:
    """API client for 46elks."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.auth = (username, password)

    async def async_get_account_info(self, hass: HomeAssistant) -> dict:
        """Get account information."""
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.get(
                    f"{API_BASE_URL}/me",
                    auth=self.auth,
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching account info: %s", err)
            return None

    async def async_get_sms_history(self, hass: HomeAssistant, limit: int = 10) -> list:
        """Get SMS history."""
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.get(
                    f"{API_BASE_URL}/sms",
                    auth=self.auth,
                    params={"limit": limit},
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching SMS history: %s", err)
            return []

    async def async_get_call_history(self, hass: HomeAssistant, limit: int = 10) -> list:
        """Get call history."""
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.get(
                    f"{API_BASE_URL}/calls",
                    auth=self.auth,
                    params={"limit": limit},
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching call history: %s", err)
            return []

    async def async_get_numbers(self, hass: HomeAssistant) -> list:
        """Get allocated phone numbers."""
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.get(
                    f"{API_BASE_URL}/numbers",
                    auth=self.auth,
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching numbers: %s", err)
            return []

    def get_mms_capable_numbers(self, numbers: list) -> list:
        """Filter for MMS-capable numbers."""
        mms_numbers = []
        for number in numbers:
            if number.get("active") == "yes" and "mms" in number.get("capabilities", []):
                mms_numbers.append(number.get("number"))
        return mms_numbers

    async def async_send_sms(
        self, hass: HomeAssistant, from_number: str, to_number: str, message: str
    ) -> dict:
        """Send an SMS."""
        data = {
            "from": from_number,
            "to": to_number,
            "message": message,
        }
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.post(
                    f"{API_BASE_URL}/sms",
                    data=data,
                    auth=self.auth,
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending SMS: %s", err)
            raise

    async def async_make_call(
        self, hass: HomeAssistant, from_number: str, to_number: str, voice_start: str
    ) -> dict:
        """Make a phone call."""
        data = {
            "from": from_number,
            "to": to_number,
            "voice_start": voice_start,
        }
        try:
            response = await hass.async_add_executor_job(
                lambda: requests.post(
                    f"{API_BASE_URL}/calls",
                    data=data,
                    auth=self.auth,
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error making call: %s", err)
            raise

    async def async_send_mms(
        self, hass: HomeAssistant, from_number: str, to_number: str, message: str = None, image: str = None
    ) -> dict:
        """Send an MMS."""
        data = {
            "from": from_number,
            "to": to_number,
        }
        if message:
            data["message"] = message
        if image:
            data["image"] = image

        try:
            response = await hass.async_add_executor_job(
                lambda: requests.post(
                    f"{API_BASE_URL}/mms",
                    data=data,
                    auth=self.auth,
                    timeout=API_TIMEOUT,
                )
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending MMS: %s", err)
            raise


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 46elks from a config entry."""
    username = entry.data[CONF_API_USERNAME]
    password = entry.data[CONF_API_PASSWORD]

    api = ElksApi(username, password)

    account_info = await api.async_get_account_info(hass)
    if account_info is None:
        raise ConfigEntryNotReady("Failed to connect to 46elks API")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_send_sms(call: ServiceCall) -> None:
        """Handle the send_sms service call."""
        from_number = call.data.get("from", entry.data.get(CONF_DEFAULT_SENDER, "HomeAssistant"))
        to_number = call.data["to"]
        message = call.data["message"]

        account_info = await api.async_get_account_info(hass)
        if account_info and float(account_info.get("balance", 0)) <= 0:
            raise HomeAssistantError("Insufficient balance to send SMS")

        try:
            _LOGGER.debug("Sending SMS - From: %s, To: %s", from_number, to_number)
            result = await api.async_send_sms(hass, from_number, to_number, message)
            _LOGGER.info("SMS sent successfully: %s", result)
        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to send SMS from '%s' to '%s': %s", from_number, to_number, err)
            raise HomeAssistantError(f"Failed to send SMS: {err}") from err

    async def handle_make_call(call: ServiceCall) -> None:
        """Handle the make_call service call."""
        from_number = call.data["from"]
        to_number = call.data["to"]
        audio_url = call.data["audio_url"]

        numbers = await api.async_get_numbers(hass)
        voice_capable = [
            num.get("number") for num in numbers
            if num.get("active") == "yes" and "voice" in num.get("capabilities", [])
        ]

        if from_number not in voice_capable:
            if voice_capable:
                raise HomeAssistantError(
                    f"The number '{from_number}' cannot make calls. "
                    f"Please use one of your voice-enabled numbers: {', '.join(voice_capable)}"
                )
            raise HomeAssistantError(
                f"The number '{from_number}' cannot make calls. "
                "You don't have any voice-enabled numbers allocated. "
                "To make calls, you need to allocate a number from 46elks. "
                "Visit https://46elks.se/allocate to get a voice-enabled number."
            )

        voice_start = json.dumps({"play": audio_url})

        account_info = await api.async_get_account_info(hass)
        if account_info and float(account_info.get("balance", 0)) <= 0:
            raise HomeAssistantError("Insufficient balance to make call")

        try:
            result = await api.async_make_call(hass, from_number, to_number, voice_start)
            _LOGGER.info("Call initiated successfully: %s", result)
        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to make call: %s", err)
            raise HomeAssistantError(f"Failed to make call: {err}") from err

    async def handle_send_mms(call: ServiceCall) -> None:
        """Handle the send_mms service call."""
        from_number = call.data["from"]
        to_number = call.data["to"]
        message = call.data.get("message")
        image = call.data.get("image")

        if not message and not image:
            raise HomeAssistantError("MMS requires either a message or an image")

        numbers = await api.async_get_numbers(hass)
        mms_capable = api.get_mms_capable_numbers(numbers)

        if from_number not in mms_capable:
            if mms_capable:
                raise HomeAssistantError(
                    f"The number '{from_number}' cannot send MMS. "
                    f"Please use one of your MMS-capable numbers instead: {', '.join(mms_capable)}"
                )
            raise HomeAssistantError(
                f"The number '{from_number}' cannot send MMS. "
                "You don't have any MMS-capable numbers allocated. "
                "To send MMS, you need to allocate a mobile number from 46elks (costs 250 SEK/month). "
                "Visit https://46elks.se/allocate to get a number with MMS capability."
            )

        account_info = await api.async_get_account_info(hass)
        if account_info and float(account_info.get("balance", 0)) <= 0:
            raise HomeAssistantError("Insufficient balance to send MMS")

        try:
            _LOGGER.debug("Sending MMS - From: %s, To: %s", from_number, to_number)
            result = await api.async_send_mms(hass, from_number, to_number, message, image)
            _LOGGER.info("MMS sent successfully: %s", result)
        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.error("Failed to send MMS from '%s' to '%s': %s", from_number, to_number, err)
            raise HomeAssistantError(f"Failed to send MMS: {err}") from err

    hass.services.async_register(DOMAIN, SERVICE_SEND_SMS, handle_send_sms, schema=SEND_SMS_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_MAKE_CALL, handle_make_call, schema=MAKE_CALL_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_SEND_MMS, handle_send_mms, schema=SEND_MMS_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
