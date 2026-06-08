import time
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto("http://127.0.0.1:8000")
    
    print("Waiting for page to load...")
    # Wait for the main UI to render
    page.wait_for_selector(".tab-content", timeout=10000)
    time.sleep(3) # Extra wait for charts to render fully
    
    print("Capturing Tab 1...")
    page.screenshot(path="slides/tab1.png", full_page=False)
    
    print("Capturing Tab 2...")
    page.get_by_text("How Healthy Is It?", exact=True).click()
    time.sleep(3)
    page.screenshot(path="slides/tab2.png", full_page=False)
    
    print("Capturing Tab 3...")
    page.get_by_text("What's In Our Food?", exact=True).click()
    time.sleep(3)
    page.screenshot(path="slides/tab3.png", full_page=False)
    
    print("Capturing Tab 4...")
    page.get_by_text("My Diet Simulator", exact=True).click()
    time.sleep(3)
    page.screenshot(path="slides/tab4.png", full_page=False)
    
    browser.close()
    print("Done!")

with sync_playwright() as playwright:
    run(playwright)
