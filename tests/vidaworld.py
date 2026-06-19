import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    drv = webdriver.Chrome(options=options)
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


def _save_screenshot(drv, name):
    try:
        out_dir = 'screenshots'
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, name)
        drv.save_screenshot(path)
        print(f'Saved screenshot: {path}')
    except Exception as e:
        print(f'Could not save screenshot: {e}')


def test_book_vida_test_ride_with_full_name(driver):
    wait = WebDriverWait(driver, 25)
    try:
        # 1. Navigate to VIDA homepage
        driver.get('https://www.vidaworld.com/')
        wait.until(EC.title_contains('VIDA'))
        assert 'VIDA' in driver.title

        # 2. Close the popup (close-button)
        try:
            close_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='close-button']")
            ))
            close_btn.click()
        except (TimeoutException, ElementClickInterceptedException):
            # Popup may not always appear
            print('Close popup not present or could not be clicked; continuing.')

        # 3. Click the Test Ride link
        test_ride_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space(text())='Test Ride' or contains(@href,'/test-ride.html')]")
        ))
        test_ride_link.click()

        # Verify navigation to test-ride page
        wait.until(EC.url_contains('/test-ride.html'))
        assert '/test-ride.html' in driver.current_url
        wait.until(EC.title_contains('Test Ride'))

        # 4. Scroll down to reveal the form
        driver.execute_script('window.scrollBy(0, 579);')
        time.sleep(0.5)

        # 5. Enter the full name
        fname_input = wait.until(EC.visibility_of_element_located((By.ID, 'fname')))
        fname_input.clear()
        fname_input.send_keys('agam singh')
        assert fname_input.get_attribute('value') == 'agam singh'

        # 6. Click Confirm
        confirm_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space(text())='Confirm' or @type='submit']")
        ))
        confirm_btn.click()

        # 7. Assert post-submit state — still on test-ride page, heading visible
        wait.until(EC.url_contains('/test-ride.html'))
        assert '/test-ride.html' in driver.current_url

        # Heading should still relate to Test Ride (either booking heading or step heading)
        heading_present = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(translate(., 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'TEST RIDE')]")
                )
            )
            heading_present = True
        except TimeoutException:
            heading_present = False
        assert heading_present, 'Expected a Test Ride related heading to be visible after Confirm.'

    except Exception as e:
        _save_screenshot(driver, 'book_vida_test_ride_failure.png')
        raise
