"""Constants for the 46elks integration."""
from datetime import timedelta

DOMAIN = "elks_46"

# Configuration
CONF_API_USERNAME = "api_username"
CONF_API_PASSWORD = "api_password"
CONF_DEFAULT_SENDER = "default_sender"

# API
API_BASE_URL = "https://api.46elks.com/a1"
API_TIMEOUT = 10

# Services
SERVICE_SEND_SMS = "send_sms"
SERVICE_SEND_MMS = "send_mms"
SERVICE_MAKE_CALL = "make_call"

# Sensor update interval
SCAN_INTERVAL = timedelta(minutes=30)
