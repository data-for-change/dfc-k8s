import sys
import time
import uuid
import datetime

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def main(username, password):
    folder_name = uuid.uuid4().hex
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": f"/var/selenium/tempdata/{folder_name}"
    })
    driver = webdriver.Remote(command_executor=f"https://{username}:{password}@selenium.dataforchange.org.il/wd/hub", options=options)
    try:
        driver.get("https://curl.se/windows/")
        time.sleep(5)
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href$='.zip']")
        assert len(elements) > 0
        element = elements[0]
        ActionChains(driver).move_to_element(element).click().perform()
        start_time = datetime.datetime.now()
        while True:
            time.sleep(1)
            if (datetime.datetime.now() - start_time).total_seconds() > 60:
                raise Exception("Timeout")
            got_folder = False
            for item in requests.get(f"https://{username}:{password}@selenium.dataforchange.org.il/tempdata/").json():
                if item['name'] == folder_name:
                    got_folder = True
                    break
            item_name = None
            if got_folder:
                for item in requests.get(f"https://{username}:{password}@selenium.dataforchange.org.il/tempdata/{folder_name}/").json():
                    if item['name'].endswith('.zip'):
                        item_name = item['name']
                        break
            if item_name:
                assert item_name.startswith('curl') and item_name.endswith('.zip')
                print(f'Got {item_name}')
                break
    finally:
        driver.quit()


if __name__ == "__main__":
    main(*sys.argv[1:])
