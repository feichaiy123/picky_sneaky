
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from dotenv import load_dotenv
import yaml
from util import *
import schedule
from datetime import date, timedelta
from tabulate import tabulate


class ScraperBot:

    def _load_preference(self):
        """Load configuration from the YAML file."""
        try:
            with open(self.config_path, "r") as file:
                return yaml.safe_load(file)
        except:
            pass
    
    def __init__(self, config_path="config.yaml", headless=False):
        """Initialize the configuration manager and load YAML."""
        self.config_path = config_path
        self.preference = self._load_preference()
        self.headless = headless
        self.target_program = self.preference['target_program']
        self._load_config()
    
    def date_manager (self): 
        self.get_target_date()
        self.target_date = ""
        weekday_number = self.target_date_original.weekday()
        (self.target_start_time, self.target_end_time) = open_play_time_formatter (self.preference['target_times'][weekday_number])
        self.rest_days = self.preference["rest_days"]
        

    def get_target_date (self): 
        # get the current date 
        current_date = date.today()
        self.target_date_original = current_date + timedelta (days=8) # TODO FIX 

    def _load_config (self):
        # load credential 
        load_dotenv()  # Load environment variables from .env file
        self.username = os.getenv("SCRAPER_USERNAME")
        self.password = os.getenv("SCRAPER_PASSWORD")


    def _init_driver (self, headless):  
        # Set Chrome options
        chrome_options = Options()
        if headless: 
            chrome_options.add_argument ("--headless")
        chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=chrome_options)


    
    def login (self):
        user_email = self.username
        user_password = self.password
        login_url = "https://roundrock.thepicklr.com/users/sign_in"
        try:
            # Open the login page
            self.driver.get(login_url)  # Replace with the actual login URL
            # Fill in the login form
            self.driver.find_element(By.ID, "user_email").send_keys(user_email)
            self.driver.find_element(By.ID, "user_password").send_keys(user_password)
            self.driver.find_element(By.NAME, "commit").click()

        except:
            pass
        finally:
            # Optional: Keep the browser open for 5 seconds and then close
            time.sleep(2)

    def scrape_programs (self):
        # Find all programs under a certain day 
        self.programs = self.get_programs ()
        # for program in programs: 
    
    def get_programs (self): 
        # Open the target page
        self.driver.get("https://roundrock.thepicklr.com/programs?facility_id=908&category=&search=&view=weekly")
        time.sleep (5)
        

        
        try: 
            date_element = self.driver.find_element(By.XPATH, "//h3[contains(@class, 'mlr5 mtb0 text semi bold flex_shrink_0')]")
            date_range = date_element.text  # Extract text: "Feb 16-22"
            date_range_start, date_range_end = extract_dates (date_range)
            week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            while self.target_date_original > date_range_end: 
                next_week_button = self.driver.find_element(By.XPATH, "//button[span[text()='next week']]")
                next_week_button.click()
                time.sleep (2)
                date_element = self.driver.find_element(By.XPATH, "//h3[contains(@class, 'mlr5 mtb0 text semi bold flex_shrink_0')]")
                date_range = date_element.text  # Extract text: "Feb 16-22"
                date_range_start, date_range_end = extract_dates (date_range)

            if date_range_start <= self.target_date_original and self.target_date_original <= date_range_end: 
                delta = (self.target_date_original - date_range_start).days
                week_day_str = week_days[delta]
                day_str = str (self.target_date_original.day)
                if len (day_str) == 1: 
                    day_str = '0' + day_str
                self.target_date = f"{day_str} {week_day_str}" 
                if week_day_str in self.rest_days: 
                    return 


        except: 
            pass


        # Find the section for the specific day (20 Thu)

        day_section = self.driver.find_element(By.XPATH, f"//h3[contains(text(), '{self.target_date}')]/following-sibling::div")

        # Find all program links under this specific day
        programs = day_section.find_elements(By.CLASS_NAME, "item.ptb15")

        # Iterate through each program and extract details
        result = []
        for index, program in enumerate(programs, start=1):
            try:
                # Extract program title
                title = program.find_element(By.TAG_NAME, "h1").text
                if title not in self.target_program: 
                    continue 
                # Extract time
                t = program.find_element(By.CLASS_NAME, "ui.text.bold.very.small.grey").text
                (start_time, end_time) = open_play_time_formatter (t)
                time_checker_result = time_checker (self.target_start_time, self.target_end_time, start_time, end_time)
                if not time_checker_result: 
                    continue 
                # Extract location
                location = program.find_element(By.CLASS_NAME, "one_liner.ui.text.greyblue").text

                # Extract program type
                program_type = program.find_element(By.CLASS_NAME, "program_label").text

                # Extract program link
                link = program.get_attribute("href")
                
                program_obj = {
                    "Program Title": title, 
                    "Time": t, 
                    "Location": location, 
                    "Program Type": program_type, 
                    "Link": link            }
                result.append (program_obj)

            except: 
                pass
        return result



    def close(self):
        """Close the browser session."""
        self.driver.quit()
        print("🚪 Browser closed.")

    def print_confirmation (self): 
        if self.booked_programs == None or len(self.booked_programs) == 0: 
            print ("Sorry! There is no program available!")
        else:
            print ("Here is a list of the booked programs. Please double check!!!")
            print(tabulate(self.booked_programs, headers="keys", tablefmt="grid"))

    def run_bot(self):

        """Trigger the bot process. Initializes and closes driver each run."""
        print(f"🕰️ Bot triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            self._init_driver(self.headless)  # Initialize driver at each run
            self.date_manager() #The target date should be calculated each day !!!
            self.login()
            self.scrape_programs()
            self.booked_programs = self.book_session()
            self.print_confirmation()
        finally:
            self.close()


    def book_session (self): 
        booked_list = []
        for program in self.programs:
            link = program['Link']
            self.driver.get (link)
            try:
                # Wait for the button to be clickable
                book_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "book_button"))
                )
                book_button.click()
            except: 
                pass


            # Find all session cards
            time.sleep (5)
            session_cards = self.driver.find_elements(By.CLASS_NAME, "ClinicSessionCardItem")

            # List to store session objects
            session_list = []

            # Iterate through each session and extract details
            for session in session_cards:
                try:
                    price = None 
                    date = None 
                    t = None 
                    status = None 
                    is_active = None
                    booked = None
                    is_waitlisted = None
                    
                    # Extract price, date, and time
                    price = session.find_element(By.CLASS_NAME, "individual-price").text
                    date = session.find_element(By.CLASS_NAME, "name").text
                    t = session.find_elements(By.CLASS_NAME, "meta")[0].text

                    # Check for reservation status
                    try:
                        status_element = session.find_element(By.CLASS_NAME, "pbc_reservation_status")
                        status = status_element.text.lower()
                    except:
                        pass

                    # Check for 'booked' status specifically
                    try:
                        booked_element = session.find_element(By.CLASS_NAME, "pbc_reservation_status_text")
                        if "booked" in booked_element.text.lower():
                            status = "booked"
                    except:
                        pass

                    # Check if session is active (clickable)
                    is_active = "active" in session.get_attribute("class")
                    is_waitlisted = "added_waitlist" in session.get_attribute("class")
                    is_booked = status == "booked"

                    # Create a session object as a dictionary
                    session_obj = {
                        "price": price,
                        "date": date,
                        "time": t,
                        "status": status,
                        "active": is_active,
                        "waitlisted": is_waitlisted,
                        "booked": is_booked
                    }

                    # Add to the list
                    session_list.append(session_obj)
                    split_date = session_obj['date'].split(' ')
                    reordered_date = f"{split_date[1]} {split_date[0]}"
                    if reordered_date == self.target_date:
                        session.click()
                        session_time = session_obj['time']
                        (start_time, end_time) = small_time_formatter(session_time)
                        if not time_checker (self.target_start_time, self.target_end_time, start_time, end_time):
                            continue 
                        try:

                            # Locate the button by text using XPath
                            try: 
                                next_button = self.driver.find_element(By.XPATH, "//span[normalize-space()='Next']")
                                if next_button: 
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    print("Successfully clicked the 'Next' button.")
                            except: 
                                pass

                            time.sleep (5)
                            try: 
                                accept_button = self.driver.find_element(By.XPATH, "//span[normalize-space()='Accept']")
                                if accept_button:
                                    self.driver.execute_script("arguments[0].click();", accept_button)
                                    print("Successfully clicked the 'accept' button.")
                            except: 
                                pass
                            

                            time.sleep (5)
                            try: 
                                    confirm_button = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ui button primary') and text()='Confirm']")  
                                    if confirm_button: 
                                        self.driver.execute_script("arguments[0].click();", confirm_button)
                                        print("Successfully clicked the 'confirm' button.")
                            except: 
                                pass
                            
                            booked_list.append ({
                                'Title': program['Program Title'], 
                                'Date': session_obj['date'], 
                                'Time': session_obj['time']
                            })
                            time.sleep(5)


                        except: 
                            pass

                except:
                    pass
        return booked_list

    def start_scheduler(self, run_time):
        print(f"⏰ Scheduling bot to run every day at {run_time}...")

        # Schedule the bot to run at the specified time
        try:
            schedule.every().day.at(run_time).do(self.run_bot)
        except: 
            pass
        # Keep the scheduler 
        # running
        # check every minute 
        while True:
            schedule.run_pending()
            time.sleep(1)

            
if __name__ == "__main__":
    bot = ScraperBot(headless=False, config_path="config.yaml")
    bot.start_scheduler("23:00") #Every day at 11:pm

