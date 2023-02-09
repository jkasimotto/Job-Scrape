# Import the necessary libraries
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set the URL of the web page you want to scrape
url = "https://webscraper.io/test-sites/e-commerce/allinone"

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()

# Go to the specified URL
driver.get(url)

# Find all the product divs on the page
product_divs = driver.find_elements(By.XPATH, '//div[@class="col-sm-4 col-lg-4 col-md-4"]')

# Loop through each product div
for product_div in product_divs:
    # Get the product name
    name = product_div.find_element(By.XPATH, './/a[@class="title"]').text

    # Get the product price
    price = product_div.find_element(By.XPATH, './/h4[@class="pull-right price"]').text

    # Print the product name and price
    print(name + ": " + price)

# Close the browser
driver.quit()
