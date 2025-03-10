from datetime import datetime
import re 
def open_play_time_formatter (time_str):
    # Split the string into start and end times
    start_time_str, end_time_str = time_str.split(" - ")

    # Convert to datetime objects
    start_time = datetime.strptime(start_time_str, "%I:%M %p")
    end_time = datetime.strptime(end_time_str, "%I:%M %p")

    return (start_time, end_time)

def extract_dates(input_str):
    # Pattern to match same-month and cross-month ranges
    pattern = r"(\w{3}) (\d+)-(?:(\w{3}) )?(\d+)"
    
    # Search for matches
    match = re.match(pattern, input_str)

    if match:
        start_month, start_day, end_month, end_day = match.groups()

        # Use the start month if end month is not specified (same-month range)
        if not end_month:
            end_month = start_month

        # Get current year
        current_year = datetime.now().year

        # Convert to datetime objects
        start_date = datetime.strptime(f"{start_month} {start_day} {current_year}", "%b %d %Y").date()
        end_date = datetime.strptime(f"{end_month} {end_day} {current_year}", "%b %d %Y").date()

        return start_date, end_date
    else:
        return None, None


def small_time_formatter (time_str):
    # TODO FIX 
    # Extract start and end times with PM
    start_time_str, end_time_str = time_str.split("-")
    start_time_value = re.search(r'\d+', start_time_str).group()
    end_time_value  = re.search(r'\d+', end_time_str).group()
    if end_time_str.endswith('pm'): 
        if start_time_value >= end_time_value:
            start_time_str += "am"
        else: 
            start_time_str += "pm"
    else: 
        start_time_str += "am"
    # Convert to datetime objects for formatting
    start_time = datetime.strptime(start_time_str, "%I%p")
    end_time = datetime.strptime(end_time_str, "%I%p")
    return (start_time, end_time)

def time_checker (target_start_time, target_end_time, start_time, end_time): 
    return start_time >= target_start_time and end_time <= target_end_time