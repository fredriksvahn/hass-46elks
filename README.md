# 46elks for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Tests](https://github.com/fredriksvahn/hass-46elks/actions/workflows/tests.yml/badge.svg)](https://github.com/fredriksvahn/hass-46elks/actions/workflows/tests.yml)
[![Validate](https://github.com/fredriksvahn/hass-46elks/actions/workflows/validate.yml/badge.svg)](https://github.com/fredriksvahn/hass-46elks/actions/workflows/validate.yml)

Home Assistant integration for [46elks](https://46elks.com) - a Swedish SMS, MMS, and Voice API service.

## Features

- 📱 Send SMS messages with customizable sender names
- 📞 Make voice calls with audio playback
- 📧 Send MMS messages (requires MMS-capable number)
- 💰 Monitor account balance and costs
- 📊 Track SMS and call history
- ✅ Automatic number capability verification

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/fredriksvahn/hass-46elks` as an Integration
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/elks_46` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "46elks"
4. Enter your 46elks API credentials:
   - **API Username**: Your 46elks API username
   - **API Password**: Your 46elks API password
   - **Default Sender** (optional): Default sender name for SMS (1-11 characters, must start with a letter)

You can find your API credentials at [dashboard.46elks.com](https://dashboard.46elks.com/).

## Usage

### Sensors

The integration provides the following sensors:

- **46elks Balance**: Current account balance in SEK
- **46elks Account**: Account information
- **46elks Last SMS**: Details of the last SMS sent
- **46elks Last Call**: Details of the last call made
- **46elks SMS Today**: Number of SMS messages sent today
- **46elks Cost Today**: Total cost of SMS and calls today in SEK

### Services

#### `elks_46.send_sms`

Send an SMS message.

```yaml
service: elks_46.send_sms
data:
  to: "+46701234567"
  message: "Hello from Home Assistant!"
  from: "MyAlert"  # Optional, uses default sender if not specified
```

#### `elks_46.make_call`

Make a voice call with audio playback.

```yaml
service: elks_46.make_call
data:
  from: "+46766865802"  # Your allocated 46elks number
  to: "+46701234567"
  audio_url: "https://yourdomain.com/alert.mp3"  # Public URL to MP3 file
```

#### `elks_46.send_mms`

Send an MMS message (requires MMS-capable number).

```yaml
service: elks_46.send_mms
data:
  from: "+46701234567"  # Your MMS-capable number
  to: "+46709876543"
  message: "Check out this image!"  # Optional if image is provided
  image: "https://yourdomain.com/snapshot.jpg"  # Optional if message is provided
```

### Example Automations

#### Motion Detection Alert

```yaml
automation:
  - alias: "Send SMS on motion"
    trigger:
      platform: state
      entity_id: binary_sensor.motion_sensor
      to: "on"
    action:
      service: elks_46.send_sms
      data:
        to: "+46701234567"
        message: "Motion detected at home!"
```

#### Camera Snapshot via MMS

```yaml
automation:
  - alias: "Send camera snapshot via MMS"
    trigger:
      platform: state
      entity_id: binary_sensor.doorbell
      to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshot.jpg"
      - service: elks_46.send_mms
        data:
          from: "+46701234567"
          to: "+46709876543"
          message: "Someone at the door!"
          image: "https://your-ha-instance.duckdns.org/local/snapshot.jpg"
```

## Requirements

- Home Assistant 2023.1 or newer
- A 46elks account ([sign up here](https://46elks.com))
- API credentials from 46elks
- For voice calls: An allocated phone number with voice capability
- For MMS: An allocated mobile number with MMS capability (250 SEK/month)

## Costs

46elks is a pay-as-you-go service:
- SMS: ~0.35 SEK per message (varies by destination)
- Voice calls: ~0.45 SEK/minute (varies by destination)
- MMS: ~2.00 SEK per message
- Phone numbers: From 20 SEK/month (voice) or 250 SEK/month (mobile with MMS)

Check current pricing at [46elks.com/pricing](https://46elks.com/pricing).

## Troubleshooting

### SMS not sending

- Verify your API credentials are correct
- Check that your sender name is 1-11 characters and starts with a letter
- Ensure you have sufficient balance

### Voice calls not working

- Verify the "from" number is allocated to your account and has voice capability
- Ensure the audio URL is publicly accessible
- Check that the audio file is in MP3 format

### MMS not sending

- Verify you have an allocated mobile number with MMS capability
- Check that you're using the correct MMS-capable number as "from"
- Ensure both message and/or image are provided

## Support

If you find this integration useful, consider supporting the development:

<a href="https://www.buymeacoffee.com/fredriksvahn" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/fredriksvahn)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Credits

This integration is not affiliated with or endorsed by 46elks AB.
