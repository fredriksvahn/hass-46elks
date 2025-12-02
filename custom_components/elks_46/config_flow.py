"""Config flow for 46elks integration."""
import logging
import re

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    API_BASE_URL,
    API_TIMEOUT,
    CONF_API_PASSWORD,
    CONF_API_USERNAME,
    CONF_DEFAULT_SENDER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def validate_sender_name(value: str) -> str:
    """Validate sender name meets 46elks requirements."""
    if not value:
        raise vol.Invalid("Sender name cannot be empty")
    if len(value) > 11:
        raise vol.Invalid("Sender name must be max 11 characters")
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", value):
        raise vol.Invalid("Sender must start with a letter and contain only letters and numbers")
    return value


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_USERNAME): str,
        vol.Required(CONF_API_PASSWORD): str,
        vol.Optional(CONF_DEFAULT_SENDER, default="ELKS46"): str,
    }
)


async def validate_credentials(hass: HomeAssistant, username: str, password: str) -> dict:
    """Validate the credentials by making a test API call."""
    try:
        response = await hass.async_add_executor_job(
            lambda: requests.get(
                f"{API_BASE_URL}/me",
                auth=(username, password),
                timeout=API_TIMEOUT,
            )
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 401:
            raise InvalidAuth
        raise CannotConnect
    except requests.exceptions.RequestException:
        raise CannotConnect


class ElksConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 46elks."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                sender = user_input.get(CONF_DEFAULT_SENDER, "ELKS46")
                if len(sender) > 11:
                    errors["default_sender"] = "Sender name must be max 11 characters"
                elif not re.match(r"^[A-Za-z][A-Za-z0-9]*$", sender):
                    errors["default_sender"] = "Sender must start with a letter and contain only letters and numbers"

                if not errors:
                    info = await validate_credentials(
                        self.hass,
                        user_input[CONF_API_USERNAME],
                        user_input[CONF_API_PASSWORD],
                    )

                    await self.async_set_unique_id(user_input[CONF_API_USERNAME])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"46elks ({info.get('displayname', user_input[CONF_API_USERNAME])})",
                        data=user_input,
                    )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
