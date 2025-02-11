
from fastapi import FastAPI 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi.middleware.cors import CORSMiddleware
import re, random, time
from fake_useragent import UserAgent



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

def setup_driver():
    PATH = "./chromedriver"
    service = Service(executable_path=PATH)
    options = Options()
    
    #Add option to run in headless mode
    options.add_argument("--headless")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--disable-gpu")
    #Add user agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    # Add options to simulate human-like behavior
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=service, options=options) 

    # Additional options to simulate human-like behavior
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver

@app.get("/search/{product_name}")
async def search_all_sites(product_name: str):
    driver = setup_driver()
    try:
        results = [
            search_newegg(driver, product_name),
            search_bestbuy(driver, product_name),
            search_walmart(driver, product_name)
        ]
    finally:
        driver.quit()
    
    return {
        "Newegg": {"Item": results[0][1], "Price": results[0][2], "URL": results[0][3]},
        "BestBuy": {"Item": results[1][1], "Price": results[1][2], "URL": results[1][3]},
        "Walmart": {"Item": results[2][1], "Price": results[2][2], "URL": results[2][3]}
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
        
    except Exception as e:
        print(f"Error: {str(e)}")
 
def clean_price(price_str):
    # Remove any non-digit, period, or comma characters
    cleaned_price = re.sub(r'[^\d.,]', '', price_str)

    # Replace commas with empty strings to remove the thousands separator
    cleaned_price = cleaned_price.replace(',', '')

    if '.' in cleaned_price:
        # If it contains a period, return the price as a float
        return float(cleaned_price)
    else:
        # If it doesn't contain a period, assume the price is in cents and divide by 100
        return float(cleaned_price) / 100
    
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
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.pricing-price  div[data-testid="large-price"] .priceView-customer-price > span:nth-child(1)'))
        ).text
        return ('Bestbuy', product, clean_price(price), product_url)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return ('Bestbuy', None, None, None)

def search_walmart(driver, product_name):   
    ua = UserAgent()
    user_agent = ua.random  # Randomize the User-Agent
    # Set the new User-Agent
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent}) 
    
    url = f'https://www.walmart.com/search/?query={product_name}'
    driver.get(url)
    
    delay = random.uniform(2, 5)  # Random delay between 2 and 5 seconds
    time.sleep(delay)
    
    try:
        product= WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[data-automation-id="product-title"]'))
        ).text
        product_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a.absolute.w-100.h-100.z-1.hide-sibling-opacity'))
        ).get_attribute('href')
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-automation-id="product-price"] div[aria-hidden="true"]'))
        ).text
        
        return ('Walmart', product, clean_price(price), product_url)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return ('Walmart', None, None, None)

def search_newegg(driver, product_name):
    url = f'https://www.newegg.com/p/pl?d={product_name}'
    driver.get(url)

    click_us_link(driver, url, "Newegg")  # Ensure this function is correctly implemented

    try:
        product_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.item-title'))
        )
        product = product_element.text
        product_url = product_element.get_attribute('href')
        price_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.price-current'))
        )
        price = price_element.text.strip().split()[0]  # Assuming the price is followed by currency or other text

        return ('Newegg', product, clean_price(price), product_url)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return ('Newegg', None, None, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)