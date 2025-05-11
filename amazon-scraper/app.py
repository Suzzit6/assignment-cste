from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

search_url = "https://www.amazon.in/s?k=soft+toys"
driver.get(search_url)
print(f"Navigating to: {search_url}")

# Wait for page to load completely
time.sleep(5)

# Scroll down to load more products
print("Scrolling to load more products...")
for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/5*{});".format(i+1))
    time.sleep(1)
    
print("Starting to scrape products...")
scraped_data = []

# Find all product cards
products = driver.find_elements(By.XPATH, "//div[contains(@data-component-type, 's-search-result')]")
print(f"Found {len(products)} products in total")
# Add this function before your main loop

    
def get_brand_from_product_page(url):
    product_driver = None # Initialize to None
    try:
        # Create a new driver for each product to avoid stale element references
        product_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        product_driver.get(url)

        # Wait for the main content area to load
        WebDriverWait(product_driver, 10).until(
            EC.presence_of_element_located((By.ID, 'centerCol'))
        )

        # Try multiple selectors where brand info might be found
        # Prioritizing the byline info selectors based on inspection
        brand_selectors = [
            (By.ID, "bylineInfo"), # Direct link with ID
            (By.CSS_SELECTOR, "#bylineInfo_feature_div a"), # Link within the feature div
            (By.XPATH, "//a[contains(@class, 'contributorNameID')]"), # Alternative class-based link
            (By.XPATH, "//span[contains(text(), 'Brand')]/following-sibling::span"), # Text label + sibling span
            (By.XPATH, "//tr[contains(.//th, 'Brand')]/td")  # From product details table
        ]

        for selector_type, selector_value in brand_selectors:
            try:
                # Use find_elements to handle cases where a selector might match multiple things,
                # although for brand, you usually expect one or zero.
                elements = product_driver.find_elements(selector_type, selector_value)
                if elements:
                    brand = elements[0].text.strip()
                    if brand and brand.lower() != 'visit the store': # Add a check for generic text like "Visit the Store"
                         # Sometimes the text is "Visit the [Brand Name] Store". Extract just the brand name.
                         if brand.startswith("Visit the ") and brand.endswith(" Store"):
                             brand = brand[len("Visit the "):-len(" Store")]
                        # some brands may have text like Brand: "Brand Name"
                    if brand.startswith("Brand: "):
                        brand = brand[len("Brand: "):]
                    # Clean up the brand name
                    brand = brand.replace("Brand: ", "").strip()
                    # Check if the brand is empty or contains generic text
                    if brand and brand.lower() != 'visit the store':
                        return brand
                    else:
                        print(f"Brand found but is generic or empty: {brand}")
                        continue
                      
                         
            except Exception as e:
                 # Catch potential StaleElementReferenceException or other issues with a specific selector
                 print(f"Error with selector {selector_value}: {e}")
                 continue # Try the next selector

        return None

    except TimeoutException:
        print(f"Timeout waiting for page to load: {url}")
        return None
    except Exception as e:
        print(f"Error getting brand for {url}: {str(e)}")
        return None
    finally:
        # Ensure the driver is closed even if an error occurs
        if product_driver:
            product_driver.quit()    
        
sponsored_count = 0
for product in products:
    try:
        # Try both common ways that Amazon marks sponsored products
        sponsored_tags = product.find_elements(By.XPATH, ".//span[contains(text(), 'Sponsored')]")
        sponsored_labels = product.find_elements(By.XPATH, ".//span[contains(@class, 'puis-sponsored-label')]")
        
        is_sponsored = len(sponsored_tags) > 0 or len(sponsored_labels) > 0
        
        # Only process sponsored products
        if not is_sponsored:
            continue
        
        sponsored_count += 1
        
        # Extract product details with better error handling
        try:
            title_element = product.find_element(By.XPATH, ".//h2/a/span")
            title = title_element.text.strip()
        except:
            try:
                title_element = product.find_element(By.XPATH, ".//h2/span")
                title = title_element.text.strip()
            except:
                title = None
        
        try:
            price_element = product.find_element(By.XPATH, ".//span[@class='a-price']/span[@class='a-offscreen']")
            price = price_element.get_attribute("innerHTML").strip()
            # Clean up the price
            price = price.replace("₹", "").replace(",", "").strip()
        except:
            price = None
        
        try:
            rating_element = product.find_element(By.XPATH, ".//span[contains(@class, 'a-icon-alt')]")
            rating = rating_element.get_attribute("innerHTML").split(" ")[0].strip()
        except:
            rating = None
        
        try:
            reviews_element = product.find_element(By.XPATH, ".//span[contains(@class, 'a-size-base') and (contains(text(), ',') or contains(text(), '('))]")
            reviews = reviews_element.text.replace(",", "").replace("(", "").replace(")", "").strip()
        except:
            reviews = "0"
        
        
        try:
             # Keep the existing XPath for the image, it looks correct
            image_element = product.find_element(By.XPATH, ".//img[contains(@class, 's-image')]")
            image = image_element.get_attribute("src")
        except:
            image = None
        
        try:
            # Refined XPath for the URL
            url_element = product.find_element(By.XPATH, ".//h2/ancestor::a")
            url = url_element.get_attribute("href")
            if url:
                import urllib.parse
                parsed_url = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if 'url' in query_params:
                    url = urllib.parse.unquote(query_params['url'][0])
                    if not url.startswith("http"):
                         url = "https://www.amazon.in" + url
                else:
                    url = "URL not found (parameter missing)"
        except:
            url = None
        
        try:
            if url != None:
                brand = get_brand_from_product_page(url)
        except:
            brand = None
        
        # Append to our results
        scraped_data.append({
            "Title": title,
            "Brand": brand,
            "Reviews": reviews,
            "Rating": rating,
            "Price": price,
            "Image": image,
            "URL": url,
            "Is_Sponsored": "Yes"
        })
        
        print(f"Scraped sponsored product: {title[:30]}..." if len(title) > 30 else f"Scraped sponsored product: {title}")
        
    except Exception as e:
        print(f"Error processing a product: {str(e)}")

# Cleanup
driver.quit()

print(f"Finished scraping. Found {sponsored_count} sponsored products out of {len(products)} total products")

# Save to CSV
if scraped_data:
    df = pd.DataFrame(scraped_data)
    output_file = "amazon_sponsored_softtoys.csv"
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file} with {len(df)} sponsored products")
else:
    print("No sponsored products found to save")
    
