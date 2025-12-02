"""Test validation logic for 46elks integration."""
import pytest
import re

from custom_components.elks_46.config_flow import validate_sender_name


class TestSenderNameValidation:
    """Test sender name validation."""

    def test_valid_sender_names(self):
        """Test valid sender names."""
        valid_names = ["ELKS46", "HomeAlert", "A", "Test123", "MyApp"]
        for name in valid_names:
            assert validate_sender_name(name) == name

    def test_too_long_sender_name(self):
        """Test sender name exceeding 11 characters."""
        with pytest.raises(Exception, match="max 11 characters"):
            validate_sender_name("ThisIsTooLong")

    def test_empty_sender_name(self):
        """Test empty sender name."""
        with pytest.raises(Exception, match="cannot be empty"):
            validate_sender_name("")

    def test_sender_starting_with_number(self):
        """Test sender name starting with number."""
        with pytest.raises(Exception, match="must start with a letter"):
            validate_sender_name("123Test")

    def test_sender_with_special_characters(self):
        """Test sender name with special characters."""
        with pytest.raises(Exception, match="only letters and numbers"):
            validate_sender_name("Test-Alert")

    def test_sender_with_spaces(self):
        """Test sender name with spaces."""
        with pytest.raises(Exception, match="only letters and numbers"):
            validate_sender_name("My App")


class TestCapabilityFiltering:
    """Test capability filtering logic."""

    def test_get_mms_capable_numbers_with_mms(self):
        """Test filtering MMS-capable numbers."""
        from custom_components.elks_46 import ElksApi

        api = ElksApi("user", "pass")
        numbers = [
            {"number": "+46701111111", "active": "yes", "capabilities": ["voice", "sms"]},
            {"number": "+46702222222", "active": "yes", "capabilities": ["voice", "sms", "mms"]},
            {"number": "+46703333333", "active": "no", "capabilities": ["voice", "sms", "mms"]},
        ]

        mms_numbers = api.get_mms_capable_numbers(numbers)
        assert len(mms_numbers) == 1
        assert "+46702222222" in mms_numbers
        assert "+46701111111" not in mms_numbers
        assert "+46703333333" not in mms_numbers  # inactive

    def test_get_mms_capable_numbers_empty(self):
        """Test filtering when no MMS-capable numbers."""
        from custom_components.elks_46 import ElksApi

        api = ElksApi("user", "pass")
        numbers = [
            {"number": "+46701111111", "active": "yes", "capabilities": ["voice", "sms"]},
        ]

        mms_numbers = api.get_mms_capable_numbers(numbers)
        assert len(mms_numbers) == 0

    def test_voice_capable_filtering(self):
        """Test filtering voice-capable numbers."""
        numbers = [
            {"number": "+46701111111", "active": "yes", "capabilities": ["sms"]},
            {"number": "+46702222222", "active": "yes", "capabilities": ["voice", "sms"]},
            {"number": "+46703333333", "active": "no", "capabilities": ["voice"]},
        ]

        voice_numbers = [
            num.get("number") for num in numbers
            if num.get("active") == "yes" and "voice" in num.get("capabilities", [])
        ]

        assert len(voice_numbers) == 1
        assert "+46702222222" in voice_numbers


class TestBalanceConversion:
    """Test balance conversion from öre to SEK."""

    def test_balance_conversion(self):
        """Test converting balance from öre to SEK."""
        balance_ore = 1974000
        balance_sek = round(balance_ore / 10000, 2)
        assert balance_sek == 197.40

    def test_zero_balance(self):
        """Test zero balance conversion."""
        balance_ore = 0
        balance_sek = round(balance_ore / 10000, 2)
        assert balance_sek == 0.00

    def test_small_balance(self):
        """Test small balance conversion."""
        balance_ore = 350  # Cost of one SMS
        balance_sek = round(balance_ore / 10000, 2)
        assert balance_sek == 0.04
