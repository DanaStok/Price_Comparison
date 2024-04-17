from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def setup_driver():
    # Path to the ChromeDriver
    PATH = "./chromedriver"  # Update this path
    service = Service(executable_path=PATH)
    options = Options()
    options.headless = True  # Enable headless mode if you don't need a browser UI
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_bestbuy(driver, product_name):
    url = f'https://www.bestbuy.com/site/searchpage.jsp?st={product_name}'
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load
    try:
        product = driver.find_element(By.CSS_SELECTOR, '.sku-header').text
        price = driver.find_element(By.CSS_SELECTOR, '.priceView-customer-price span').text
        return 'Bestbuy', product, price
    except:
        return 'Bestbuy', None, None

def search_walmart(driver, product_name):
    url = f'https://www.walmart.com/search/?query={product_name}'
    driver.get(url)
    time.sleep(3)
    try:
        product = driver.find_element(By.CSS_SELECTOR, '.search-result-product-title span').text
        price = driver.find_element(By.CSS_SELECTOR, '.price-group').text
        return 'Walmart', product, price
    except:
        return 'Walmart', None, None

def search_newegg(driver, product_name):
    url = f'https://www.newegg.com/p/pl?d={product_name}'
    driver.get(url)
    time.sleep(3)
    try:
        product = driver.find_element(By.CSS_SELECTOR, '.item-title').text
        price = driver.find_element(By.CSS_SELECTOR, '.price-current').text
        return 'Newegg', product, price
    except:
        return 'Newegg', None, None

def main(product_name):
    driver = setup_driver()
    results = [
        search_bestbuy(driver, product_name),
        search_walmart(driver, product_name),
        search_newegg(driver, product_name)
    ]
    driver.quit()  # Always close the driver
    
    for result in results:
        print('Site:', result[0], 'Item title:', result[1], 'Price:', result[2])

if __name__ == "__main__":
    product_name = input("Enter the product name: ")
    main(product_name)
