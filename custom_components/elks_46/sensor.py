"""Sensor platform for 46elks integration."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 46elks sensors based on a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]

    async def async_update_data():
        """Fetch data from API."""
        account_info = await api.async_get_account_info(hass)
        if account_info is None:
            raise UpdateFailed("Failed to fetch account info")

        sms_history = await api.async_get_sms_history(hass, limit=10)
        call_history = await api.async_get_call_history(hass, limit=10)

        return {
            "account": account_info,
            "sms_history": sms_history,
            "call_history": call_history,
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="46elks account",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            ElksBalanceSensor(coordinator, entry),
            ElksAccountSensor(coordinator, entry),
            ElksLastSmsSensor(coordinator, entry),
            ElksLastCallSensor(coordinator, entry),
            ElksSmsTodaySensor(coordinator, entry),
            ElksCostTodaySensor(coordinator, entry),
        ]
    )


class ElksBalanceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for 46elks account balance."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_balance"
        self._attr_name = "46elks Balance"
        self._attr_native_unit_of_measurement = "SEK"
        self._attr_icon = "mdi:currency-usd"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "account" in self.coordinator.data:
            balance_ore = float(self.coordinator.data["account"].get("balance", 0))
            return round(balance_ore / 10000, 2)
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data and "account" in self.coordinator.data:
            return {
                "currency": self.coordinator.data["account"].get("currency", "SEK"),
                "account_id": self.coordinator.data["account"].get("id"),
            }
        return {}


class ElksAccountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for 46elks account information."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_account"
        self._attr_name = "46elks Account"
        self._attr_icon = "mdi:account"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "account" in self.coordinator.data:
            return self.coordinator.data["account"].get("displayname", "Unknown")
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data and "account" in self.coordinator.data:
            account = self.coordinator.data["account"]
            balance_ore = float(account.get("balance", 0))
            return {
                "account_id": account.get("id"),
                "email": account.get("email"),
                "mobile_number": account.get("mobilenumber"),
                "balance": round(balance_ore / 10000, 2),
                "currency": account.get("currency", "SEK"),
            }
        return {}


class ElksLastSmsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for last SMS sent."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_sms"
        self._attr_name = "46elks Last SMS"
        self._attr_icon = "mdi:message-text"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "sms_history" in self.coordinator.data:
            sms_list = self.coordinator.data["sms_history"]
            if sms_list and len(sms_list) > 0:
                return sms_list[0].get("created", "Unknown")
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data and "sms_history" in self.coordinator.data:
            sms_list = self.coordinator.data["sms_history"]
            if sms_list and len(sms_list) > 0:
                last_sms = sms_list[0]
                cost_ore = float(last_sms.get("cost", 0))
                return {
                    "to": last_sms.get("to"),
                    "from": last_sms.get("from"),
                    "message": last_sms.get("message", "")[:100],
                    "status": last_sms.get("status"),
                    "cost": round(cost_ore / 10000, 2),
                    "direction": last_sms.get("direction"),
                }
        return {}


class ElksLastCallSensor(CoordinatorEntity, SensorEntity):
    """Sensor for last call made."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_call"
        self._attr_name = "46elks Last Call"
        self._attr_icon = "mdi:phone"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and "call_history" in self.coordinator.data:
            call_list = self.coordinator.data["call_history"]
            if call_list and len(call_list) > 0:
                return call_list[0].get("created", "Unknown")
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data and "call_history" in self.coordinator.data:
            call_list = self.coordinator.data["call_history"]
            if call_list and len(call_list) > 0:
                last_call = call_list[0]
                cost_ore = float(last_call.get("cost", 0))
                return {
                    "to": last_call.get("to"),
                    "from": last_call.get("from"),
                    "duration": last_call.get("duration", 0),
                    "state": last_call.get("state"),
                    "cost": round(cost_ore / 10000, 2),
                    "direction": last_call.get("direction"),
                }
        return {}


class ElksSmsTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for SMS count today."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sms_today"
        self._attr_name = "46elks SMS Today"
        self._attr_icon = "mdi:message-badge"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        from datetime import datetime, timezone

        if self.coordinator.data and "sms_history" in self.coordinator.data:
            sms_list = self.coordinator.data["sms_history"]
            today = datetime.now(timezone.utc).date()
            count = 0
            for sms in sms_list:
                created_str = sms.get("created", "")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        if created.date() == today:
                            count += 1
                    except (ValueError, AttributeError):
                        pass
            return count
        return 0


class ElksCostTodaySensor(CoordinatorEntity, SensorEntity):
    """Sensor for total cost today."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_cost_today"
        self._attr_name = "46elks Cost Today"
        self._attr_native_unit_of_measurement = "SEK"
        self._attr_icon = "mdi:cash"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="46elks Account",
            manufacturer="46elks",
            model="SMS & Voice API",
            configuration_url="https://dashboard.46elks.com/",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        from datetime import datetime, timezone

        if not self.coordinator.data:
            return 0

        today = datetime.now(timezone.utc).date()
        total_cost = 0

        if "sms_history" in self.coordinator.data:
            for sms in self.coordinator.data["sms_history"]:
                created_str = sms.get("created", "")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        if created.date() == today:
                            total_cost += float(sms.get("cost", 0))
                    except (ValueError, AttributeError):
                        pass

        if "call_history" in self.coordinator.data:
            for call in self.coordinator.data["call_history"]:
                created_str = call.get("created", "")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                        if created.date() == today:
                            total_cost += float(call.get("cost", 0))
                    except (ValueError, AttributeError):
                        pass

        return round(total_cost / 10000, 2)
