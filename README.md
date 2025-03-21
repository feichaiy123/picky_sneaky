# Automated Booking Script

This script automates the process of booking pickleball sessions using Selenium and Chrome.

## Prerequisites
- Python 3.x
- Google Chrome
- ChromeDriver (compatible with your Chrome version)
- Selenium
- dotenv
- YAML


## Installing Selenium and Setting Up Chrome
1. Install Selenium:
   ```sh
   pip install selenium
   ```

2. Install Google Chrome:
   - Download and install Google Chrome from [here](https://www.google.com/chrome/).


## Configuration

### Environment Variables
Create a `.env` file in the root directory and add your login credentials in the following format:
```
SCRAPER_USERNAME="your_username"
SCRAPER_PASSWORD="your_password"
```

### Booking Schedule
Create or modify the `config.yaml` file to set your target programs, preferred booking times, and rest days. Example:
```yaml
# Programs to target for booking
target_program:
  - "Level 2 Open Play(2.75-3.5)"
  - "Level 3 Open Play(3.5-4.0)"
  - "All Levels Open Play"

# Desired booking time range
target_times:
  - "5:00 PM - 9:00 PM"
  - "5:00 PM - 9:00 PM"
  - "5:00 PM - 9:00 PM"
  - "5:00 PM - 9:00 PM"
  - "5:00 PM - 9:00 PM"
  - "10:00 AM - 6:00 PM"
  - "10:00 AM - 6:00 PM"

add_to_waitlist: "False"

rest_days: 
  - "Sun"
```

## Usage
Run the script with:
```sh
python main.py
```

## Notes
- Ensure Chrome and ChromeDriver are installed and properly set up.
- If encountering issues, check ChromeDriver compatibility with your Chrome version.
- The script will follow your schedule as per `config.yaml`.

## Troubleshooting
- If login fails, check your credentials in the `.env` file.
- If elements are not found, inspect the website for updates that may require script adjustments.

## Disclaimer
Use this script responsibly and ensure compliance with the website's terms of service.

