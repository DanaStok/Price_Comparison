from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


app = FastAPI()

def setup_driver():
    # Path to the ChromeDriver
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
        "BestBuy": {"Item": results[0][1], "Price": results[0][2]},
        "Walmart": {"Item": results[1][1], "Price": results[1][2]},
        "Newegg": {"Item": results[2][1], "Price": results[2][2]}
    }
    
def click_us_link(driver, url, website):
    try:
        driver.get(url)
        
        if website == "Best_Buy":
            condition = EC.element_to_be_clickable((By.XPATH, "//a[@class='us-link']/h4[text()='United States']"))
        elif website == "Newegg":
            condition = EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.button.button-m.bg-white'))
        
        # Wait for the element to be clickable or visible and then click it
        us_link = WebDriverWait(driver, 10).until(condition)
        us_link.click()
        print("Clicked on the United States link successfully!")
    except Exception as e:
        print(f"The United States link was not clickable or not found within the timeout period: {str(e)}")
        
        
def search_bestbuy(driver, product_name):
    url = f'https://www.bestbuy.com/site/searchpage.jsp?st={product_name}'
    driver.get(url)
    click_us_link(driver,url,"Best_Buy")
    
    try:
        product = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.sku-title a .nc-product-title'))
        ).text
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.priceView-hero-price priceView-customer-price span[aria-hidden="true"]'))
        ).text
        return ('Bestbuy', product, price)
    except:
        return ('Bestbuy', None, None)

def search_walmart(driver, product_name):
    url = f'https://www.walmart.com/search/?query={product_name}'
    driver.get(url)
    try:
        product = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span[data-automation-id="product-title"]'))
        ).text
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-automation-id="product-price"] div[aria-hidden="true"]'))
        ).text
        return ('Walmart', product, price)
    except:
        return ('Walmart', None, None)

def search_newegg(driver, product_name):
    url = f'https://www.newegg.com/p/pl?d={product_name}'
    driver.get(url)
    click_us_link(driver,url,"Newegg")
    
    try:
        product = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.item-title'))
        ).text
        price = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.price-current'))
        ).text
        return ('Newegg', product, price)
    except:
        return ('Newegg', None, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)