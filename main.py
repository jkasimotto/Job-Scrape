# A selenium scraper that scrapes 'https://au.indeed.com/jobs?q=electrical+apprentice&l=&from=searchOnHP&vjk=160622cf4a81f104'

# Import the necessary libraries
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import undetected_chromedriver as uc

# Set the URL of the web page you want to scrape
url = "https://au.indeed.com/jobs?q=electrical+apprentice&l=&from=searchOnHP&vjk=160622cf4a81f104"
url = "https://au.indeed.com/jobs?q=electrical+apprentice&l=Sydney+NSW&vjk=409bebad85cbf336"
url = "https://au.indeed.com/jobs?q=electrical+apprentice&l=Sydney+NSW&start=60&pp=gQBaAAAAAAAAAAAAAAAB8L2LeAA4AQEBEAXDTXsoBj8-Cz9W6-zc1-sYkvixTEBaq0daUgAiITC-jB-n6E5_793sMpTg8ITDd4E8lF4AAA&vjk=f3e95885d3535abd"


class JobHeader:
    # Contains the job title, company name and location
    def __init__(self, job_title, company_name, location):
        self.job_title = job_title
        self.company_name = company_name
        self.location = location

    def __str__(self):
        return f"{self.job_title}, {self.company_name}, {self.location}"


class Job:

    # Contains the job title, company name, location and job description
    def __init__(self, job_title, company_name, location, job_description):
        self.job_title = job_title
        self.company_name = company_name
        self.location = location
        self.job_description = job_description

    def __str__(self):
        return f"{self.job_title}, {self.company_name}, {self.location}, {self.job_description}"

    def from_job_header_and_job_description(job_header, job_description):
        # Create a new Job object from a JobHeader object and a job description
        return Job(
            job_header.job_title,
            job_header.company_name,
            job_header.location,
            job_description,
        )

    def to_dict(self):
        # Return a dictionary representation of the Job object
        return {
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location": self.location,
            "job_description": self.job_description,
        }

    def to_csv_appropriate_dict(self):
        # Return a dictionary representation of the Job object
        # Replace newlines with spaces and commas with semicolons
        return {
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location": self.location.replace("\n", " ").replace(",", ";"),
            "job_description": self.job_description.replace("\n", " ").replace(
                ",", ";"
            ),
        }


def wait_for_job_cards_to_load(driver):
    # Job cards are <td> elements with class 'resultContent'
    # Wait for the page to load
    try:
        # Wait for the job cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//td[@class="resultContent"]'))
        )
    except TimeoutException:
        # If the job cards don't load, print an error message
        print("Timed out waiting for page to load")
        # Close the browser
        driver.quit()


def get_job_cards(driver):
    # The jobsearch-ResultsList <ul> element contains all the job cards
    # Get the jobsearch-ResultsList <ul> element
    results_list = driver.find_element(
        By.XPATH, '//ul[@class="jobsearch-ResultsList css-0"]'
    )

    # Every job card is a div in a <li> element in the jobsearch-ResultsList <ul> element
    # Find all the <li>/div elements in the jobsearch-ResultsList <ul> element
    job_cards = results_list.find_elements(By.XPATH, ".//li/div")

    # Find all job cards on the page.
    # One specific job card has XPath //*[@id="mosaic-provider-jobcards"]/ul/li[3]/div
    job_cards = driver.find_elements(By.XPATH, '//td[@class="resultContent"]')
    # job_cards = driver.find_elements(By.XPATH, '//td[@class="cardOutline"]')
    return job_cards


def get_job_title_or_none(job_card):
    # The job title class is a <h2> element with class 'jobTitle'
    # Sometimes the job title is missing, so we need to check for it
    try:
        # The job title class is a <h2> element with class 'jobTitle'
        job_title = job_card.find_element(
            By.XPATH, './/h2[@class="jobTitle css-1h4a4n5 eu4oa1w0"]'
        ).text
    except:
        # If the job title is missing, return None
        print("Job title not found")
        return None
    print(job_title)
    return job_title


def get_company_name(job_card):
    # The company name sits in a span underneath the job card with class 'companyName'
    company_name = job_card.find_element(By.XPATH, './/span[@class="companyName"]').text
    return company_name


def get_location(job_card):
    # The location sits in a span underneath the job card with class 'companyLocation'
    location = job_card.find_element(By.XPATH, './/div[@class="companyLocation"]').text
    return location


def get_job_header(job_card):
    # Get the job title, company name and location
    job_title = get_job_title_or_none(job_card)
    if job_title is None:
        return None
    company_name = get_company_name(job_card)
    location = get_location(job_card)
    return JobHeader(job_title, company_name, location)


def wait_for_right_pane_to_load(driver):
    # Wait for the job description to load
    try:
        # Wait for the job description to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="jobsearch-RightPane"]')
            )
        )
    except TimeoutException:
        # If the job description doesn't load, print an error message
        print("Timed out waiting for page to load")
        # Close the browser
        driver.quit()


def get_right_pane(driver):
    wait_for_right_pane_to_load(driver)
    # Get the right pane
    right_pane = driver.find_element(By.XPATH, '//div[@class="jobsearch-RightPane"]')
    return right_pane


def get_job_description(driver, right_pane):
    # Wait for the job description text to load
    try:
        # Wait for the job description text to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, './/div[@id="jobDescriptionText"]')
            )
        )
    except TimeoutException:
        # If the job description text doesn't load, print an error message
        print("Timed out waiting for page to load")
        # Close the browser
        driver.quit()

    # The job description text is in a div with id 'jobDescriptionText'.
    job_description = right_pane.find_element(
        By.XPATH, './/div[@id="jobDescriptionText"]'
    ).text

    return job_description


def get_job(driver, job_card):
    # Get the job header
    job_header = get_job_header(job_card)
    if job_header is None:
        return None

    # Click on the job card to open the job description
    job_card.click()

    # Get the right pane
    right_pane = get_right_pane(driver)

    # Scroll within the right pane to the bottom
    driver.execute_script(
        "arguments[0].scrollIntoView();", right_pane
    )

    # Wait a random number of seconds between 1 and 3
    time.sleep(random.randint(1, 3))

    # # Get the job description pane
    # job_description_pane = right_pane.find_element(
    #     By.XPATH, './/div[@class="jobsearch-jobDescriptionText"]'
    # )

    # Get the job description
    job_description = get_job_description(driver, right_pane)

    # Create a Job object
    job = Job.from_job_header_and_job_description(job_header, job_description)

    return job



# Create a new instance of the Chrome driver
driver = webdriver.Chrome()
# driver = uc.Chrome(use_subprocess=True)
wait = WebDriverWait(driver, 20)

# Go to the specified URL
driver.get(url)

# Get existing jobs
existing_jobs = pd.read_csv("jobs.csv")

# We are going to store job title, company name, location and job description in a list of dictionaries
jobs = []

# We are going to scrape 10 pages of jobs and then stop and save the data to a CSV file
# Our connection may be lost if we scrape too quickly, so we are going to wait 5 seconds between each page
# If our connection is lost, we will handle the exception and save the data to a CSV file
try:
    for i in range(10):

        wait_for_job_cards_to_load(driver)
        job_cards = get_job_cards(driver)

        # Loop through each job card
        for job_card in job_cards:
            job = get_job(driver, job_card)
            if job is None:
                continue
            if job.job_title in existing_jobs["job_title"].values and job.company_name in existing_jobs["company_name"].values:
                continue
            jobs.append(job.to_csv_appropriate_dict())

        # Scroll down to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Click on the next button to go back to the search results page
        # If the next button is missing, we are on the last page and we should stop
        try:
            # Find the next button
            next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next Page"]')
        except:
            # If the next button is missing, break out of the loop
            break

        # Click on the next button
        next_button.click()


        # Wait for the next page to load
        try:
            # Wait for the next page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//td[@class="resultContent"]')
                )
            )
        except TimeoutException:
            # If the next page doesn't load, print an error message
            print("Timed out waiting for page to load")
            # Close the browser
            driver.quit()

        # Sometimes when a new page loads a popup with a close button appears
        # If the popup appears, click on the close button
        try:
            # Find the close button
            close_button = driver.find_element(By.XPATH, '//button[@aria-label="close"]')
            # Click on the close button
            close_button.click()
        except:
            # If the close button is missing, do nothing
            pass

        # Wait five seconds
        # time.sleep(5)

except Exception as e:
    # If anything goes wrong, print an error message
    print(e)
    print("Something went wrong. Saving data to CSV file.")

input()
# Close the browser
driver.quit()

# Import the pandas library

# Create a dataframe from the list of dictionaries
df = pd.DataFrame(jobs)

# Merge the existing jobs with the new jobs
df = pd.concat([existing_jobs, df], ignore_index=True)

# Save the dataframe to a CSV file
df.to_csv("jobs.csv", index=False)

# Print the number of jobs scraped
print("Scraped " + str(len(jobs)) + " jobs")

# Print the first 5 rows of the dataframe
print(df.head())

# Print the last 5 rows of the dataframe
print(df.tail())

# Print the shape of the dataframe
print(df.shape)

# Print the number of unique company names
print(f"Unique companies: {df['company_name'].nunique()}")
