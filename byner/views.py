from django.http import StreamingHttpResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import datetime


def index(request):
    def generate():
        try:
            # Initialize the driver and configure options
            driver_path = r"C:\www\geckodriver.exe"
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            service = Service(driver_path)
            driver = webdriver.Firefox(service=service, options=firefox_options)

            # Target URL
            url = "https://binarybot.live/ldp/"
            driver.get(url)

            # Time limit for scraping: 15 minutes
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(minutes=15)

            red_numbers = []
            blue_numbers = []
            all_numbers = []
            index_counter = 1  # Initialize the index counter

            while datetime.datetime.now() < end_time:
                try:
                    digits_div = driver.find_element(By.ID, "digits")
                    spans = digits_div.find_elements(By.TAG_NAME, "span")

                    # Reset the index every 3 seconds
                    index_reset_time = datetime.datetime.now()
                    indices = []

                    for span in spans:
                        number = span.text.strip()  # Ensure 'number' has a value
                        if number:  # Only consider non-empty values
                            all_numbers.append(number)
                            if "digits_moved_up" in span.get_attribute("class"):  # Blue
                                blue_numbers.append(number)
                            elif "digits_moved_down" in span.get_attribute("class"):  # Red
                                red_numbers.append(number)

                            # Track indices within the 3-second period
                            indices.append(f"{index_counter}:{number}")
                            index_counter += 1  # Increment index

                    # Prepare and send the data to the client
                    yield f"all: {', '.join(all_numbers)}\n"
                    yield f"red: {', '.join(red_numbers)}\n"
                    yield f"blue: {', '.join(blue_numbers)}\n"
                    yield f"indices: {', '.join(indices)}\n\n"

                    # Sleep for 3 seconds before the next scrape
                    time.sleep(3)

                except Exception as e:
                    print("Error:", e)
                    break  # Exit the loop if an error occurs

            driver.quit()

        except Exception as e:
            print("Error occurred:", e)
            yield "An error occurred during scraping.\n"

    # Create a StreamingHttpResponse and set appropriate headers for Server-Sent Events (SSE)
    return StreamingHttpResponse(generate(), content_type='text/event-stream')
