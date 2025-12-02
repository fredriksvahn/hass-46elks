# 46elks Integration

Send SMS, make calls, and send MMS messages using the 46elks API.

## Features

- 📱 Send SMS with custom sender names
- 📞 Make voice calls with audio playback
- 📧 Send MMS (requires MMS-capable number)
- 💰 Monitor balance and costs
- 📊 Track message and call history

## Setup

You'll need:
- 46elks API credentials from [dashboard.46elks.com](https://dashboard.46elks.com/)
- Sufficient account balance
- For calls: An allocated phone number
- For MMS: An MMS-capable mobile number (250 SEK/month)

## Configuration

1. Enter your API username and password
2. Set a default sender name (optional, 1-11 characters)
3. Integration will verify credentials and set up sensors

## Services

- `elks_46.send_sms` - Send text messages
- `elks_46.make_call` - Make voice calls with audio
- `elks_46.send_mms` - Send MMS with images

Perfect for alerts, notifications, and automation triggers!
