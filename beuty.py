from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import datetime
from mongodb_model import MongoDB  # Import the MongoDB model

# Encode the username and password
username = "cypsolabs"
password = "@testing01"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# Construct the MongoDB URI
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@byner.vxp0o.mongodb.net/?retryWrites=true&w=majority&appName=byner"

# MongoDB configuration
DB_NAME = "testdb"
COLLECTION_NAME = "sequence_numbers"
COLLECTION_NAME2 = "last_index"

def generate():
    try:
        # Initialize MongoDB connection
        db = MongoDB(MONGO_URI, DB_NAME, COLLECTION_NAME)
        db2 = MongoDB(MONGO_URI, DB_NAME, COLLECTION_NAME2)

        last_entry = db2.fetch_data_by_query({"last_index":{"$exists":True}})
        last_index = last_entry[0]["last_index"] if last_entry else 0

        index_counter = last_index+1

        # Configure Selenium driver
        driver_path = r"C:\www\geckodriver.exe"
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        service = Service(driver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)

        # Target URL
        url = "https://binarybot.live/ldp/"
        driver.get(url)

        # Set the scraping time limit (15 minutes)
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=120)
        
        last_timestamp = None 

        while datetime.datetime.now() < end_time:
            try:
                digits_div = driver.find_element(By.ID, "digits")
                spans = digits_div.find_elements(By.TAG_NAME, "span")
                
                # Initialize the scraped data dictionary
                scraped_data = {
                    "timestamp": datetime.datetime.now(),
                    "all_numbers": [],
                    "red_numbers": [],
                    "blue_numbers": [],
                    "indices" : [],
                    "red_indices" : [],
                    "blue_indices" : [],
                    "time_intervals": [],
                    "trends": [],
                    "market_indicators": []
                }
                last_index = None
                last_number =None

                for span in spans:
                    number = span.text.strip()
                    if number:
                        scraped_data["all_numbers"].append(number)

                        # Track indices for red and blue numbers separately
                        if "digits_moved_up" in span.get_attribute("class"):  # Blue
                            scraped_data["blue_numbers"].append(number)
                            scraped_data["blue_indices"].append(f"{index_counter}:{number}")
                        elif "digits_moved_down" in span.get_attribute("class"):  # Red
                            scraped_data["red_numbers"].append(number)
                            scraped_data["red_indices"].append(f"{index_counter}:{number}")

                        # Track all indices
                        scraped_data["indices"].append(f"{index_counter}:{number}")

                        # Time Interval Calculation
                        if last_timestamp:  # Calculate the interval only if last_timestamp is set
                            time_interval = (scraped_data["timestamp"] - last_timestamp).total_seconds()
                            scraped_data["time_intervals"].append(time_interval)
                        
                        # Trend Calculation: Check if the number is increasing or decreasing
                        if last_number is not None:
                            trend = "increasing" if int(number) > int(last_number) else "decreasing"
                            scraped_data["trends"].append(trend)

                        # Check for visible market condition and fetch its exact text only for time-series entries
                        if last_timestamp is not None and (scraped_data["timestamp"] - last_timestamp).total_seconds() >= 10:  # Example condition to collect market indicators (every 10 seconds)
                            try:
                                market_condition_element = driver.find_element(By.ID, "market_condition")
                                market_condition_text = market_condition_element.text.strip()  # Get the exact text

                                if market_condition_text:  # If there's any text, append it to the market indicators
                                    scraped_data["market_indicators"].append(market_condition_text)

                            except Exception as e:
                                # If the market condition element is not found, continue without appending
                                print("Market condition not found, skipping this entry.")
                                pass

                        last_timestamp = scraped_data["timestamp"]
                        last_index = index_counter
                        last_number = number

                        index_counter += 1

                # Save the data to MongoDB
                db.insert_data(scraped_data)
                        

                # Print/log the data for debugging
                yield f"Scraped at {scraped_data['timestamp']}:\n"
                yield f"All: {', '.join(scraped_data['all_numbers'])}\n"
                yield f"Red: {', '.join(scraped_data['red_numbers'])}\n"
                yield f"Blue: {', '.join(scraped_data['blue_numbers'])}\n\n"
                yield f"indices: {', '.join(scraped_data['indices'])}\n\n"
                yield f"Red Indices: {', '.join(scraped_data['red_indices'])}\n\n"
                yield f"Blue Indices: {', '.join(scraped_data['blue_indices'])}\n\n"
                yield f"Time Intervals: {', '.join(map(str, scraped_data['time_intervals']))}\n\n"
                yield f"Trends: {', '.join(scraped_data['trends'])}\n\n"
                yield f"Market Indicators: {', '.join(scraped_data['market_indicators'])}\n\n"


                # Sleep before the next scrape
                time.sleep(12)

                

            except Exception as e:
                yield f"Error during scraping: {e}\n"
                break

        driver.quit()
        db.close_connection()
        try:
             if last_number and last_index:
                 last = {
                     "last_index": last_index,
                     "last_number": last_number
                 }
                 #db2 = MongoDB(MONGO_URI, DB_NAME, COLLECTION_NAME2)
                 db2.collection.delete_many({"last_index": {"$exists":True}})
                 db2.insert_data(last)

        except Exception as e:
             yield f"Error saving last index and number: {e}\n"
        


    except Exception as e:
        yield f"Error occurred during initialization: {e}\n"

# Example usage
if __name__ == "__main__":
    for data in generate():
        print(data)
