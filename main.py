from fastapi import FastAPI 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi.middleware.cors import CORSMiddleware
import re


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows all origins for the Next.js server
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def setup_driver():
    # Path to the ChromeDriverpip install fastapi uvicorn

    PATH = "./chromedriver"  # Update this path
    service = Service(executable_path=PATH)
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=service, options=options)
    return driver

@app.get("/search/{product_name}")
async def search_all_sites(product_name: str):
    driver = setup_driver()
    try:
        results = [
            search_bestbuy(driver, product_name),
            search_walmart(driver, product_name),
            search_newegg(driver, product_name)
        ]
    finally:
        driver.quit()
    
    return {
        "BestBuy": {"Item": results[0][1], "Price": results[0][2], "URL": results[0][3]},
        "Walmart": {"Item": results[1][1], "Price": results[1][2], "URL": results[1][3]},
        "Newegg": {"Item": results[2][1], "Price": results[2][2], "URL": results[2][3]}
    }
    
def click_us_link(driver, url, website):
    try:
        driver.get(url)
        
        if website == "BestBuy":
            condition = EC.element_to_be_clickable((By.XPATH, "//a[@class='us-link']/h4[text()='United States']"))
        elif website == "Newegg":
            condition = EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.button.button-m.bg-white'))
        
        # Wait for the element to be clickable or visible and then click it
        us_link = WebDriverWait(driver, 10).until(condition)
        us_link.click()
        print("Clicked on the United States link successfully!")
    except Exception as e:
        print(f"The United States link was not clickable or not found within the timeout period: {str(e)}")
        

def clean_price(price_str):
    # This regular expression removes any characters that are not digits, period, or comma
    clean_price = re.sub(r'[^\d.,]', '', price_str)
    return clean_price
    
def search_bestbuy(driver, product_name):
    url = f'https://www.bestbuy.com/site/searchpage.jsp?st={product_name}'
    driver.get(url)
    click_us_link(driver,url,"BestBuy")
    
    try:
        product_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.sku-title a'))
        )
        product = product_element.text
        product_url = product_element.get_attribute('href')
        print(f"BestBuy URL: {product_url}")
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.pricing-price  div[data-testid="large-price"] .priceView-customer-price > span:nth-child(1)'))
        ).text
        return ('Bestbuy', product, clean_price(price), product_url)
    except:
        return ('Bestbuy', None, None, None)

def search_walmart(driver, product_name):
    url = f'https://www.walmart.com/search/?query={product_name}'
    driver.get(url)
    try:
        product= WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[data-automation-id="product-title"]'))
        ).text
        product_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.absolute.w-100.h-100.z-1.hide-sibling-opacity'))
        ).get_attribute('href')
        print(f"Walmart URL: {product_url}")
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-automation-id="product-price"] div[aria-hidden="true"]'))
        ).text
        return ('Walmart', product, clean_price(price), product_url)
    except:
        return ('Walmart', None, None, None)

def search_newegg(driver, product_name):
    url = f'https://www.newegg.com/p/pl?d={product_name}'
    driver.get(url)
    click_us_link(driver,url,"Newegg")
    
    try:
        product_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.item-title'))
        )
        product = product_element.text
        product_url = product_element.get_attribute('href')
        print(f"Newegg URL: {product_url}")
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.price-current'))
        ).text
        return ('Newegg', product, clean_price(price), product_url)
    except:
        return ('Newegg', None, None, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)