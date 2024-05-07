import time
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import config


# Define browser webdriver
def startBrowser(name, signin):
    name = name.lower()
    try:
        if name == "firefox" or name == "ff":
            from selenium.webdriver.firefox.service import (
                Service as FirefoxService,
            )
            from webdriver_manager.firefox import GeckoDriverManager

            options = webdriver.FirefoxOptions()

            service_args = []
            if config.headless:
                service_args.extend(["-headless"])
            if config.signin:
                service_args.extend(
                    [
                        "--profile-root",
                        "C:\\Users\\KIIT\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\m4uxrhos.default-release",
                    ]
                )
                options.add_argument("--profile-root")
                options.add_argument(
                    "C:\\Users\\KIIT\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\m4uxrhos.default-release"
                )
            driver = webdriver.Firefox(
                service=FirefoxService(
                    GeckoDriverManager().install(),
                    options=options,
                    service_args=service_args,
                )
            )
        elif name == "chrome" or name == "gc":
            from selenium.webdriver.chrome.service import (
                Service as ChromeService,
            )
            from webdriver_manager.chrome import ChromeDriverManager

            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-logging")
            if config.headless:
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
            if signin:
                options.add_argument(
                    "--user-data-dir=C:\\Users\\KIIT\\AppData\\Local\\Google\\Chrome\\User Data"
                )
                options.add_argument(r"--profile-directory=Default")
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options,
            )
        elif name == "edge":
            driver = webdriver.Ie()
        elif name == "safari" or name == "sf":
            driver = webdriver.Safari()
        elif name == "explorer" or name == "ie":
            driver = webdriver.Edge()
        return driver
    except Exception as msg:
        print("Could not find this browser.")
        print(msg)


# Writing to CSV file
def save_to_csv(data):
    with open("profiles.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


def main():
    try:
        driver = startBrowser("gc", signin=config.signin)
        time.sleep(5)
        profile_data = []
        first_name = input("\nEnter First Name:")
        last_name = input("\nEnter Last Name:")

        if not config.signin:
            url = f"https://www.linkedin.com/pub/dir?firstName={first_name}&lastName={last_name}&trk=people-guest_people-search-bar_search-submit"
        else:
            # url = f"https://www.linkedin.com/search/results/people/?keywords={first_name}%20{last_name}&origin=CLUSTER_EXPANSION&sid=HIx"
            url = f"https://www.linkedin.com/search/results/people/?keywords={first_name}%20{last_name}&origin=GLOBAL_SEARCH_HEADER&sid=WYP"

        if driver:
            driver.get(url)
        else:
            return False
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)

        if not config.signin:
            main_container = driver.find_element(
                By.XPATH, "//main[@id='main-content']/section/ul"
            )
            results = main_container.find_elements(By.TAG_NAME, "li")
            print("Results found: ", len(results))
            for result in results:
                profile_ele = result.find_element(By.TAG_NAME, "a")
                profile_link = str(profile_ele.get_attribute("href"))
                profile_title = str(
                    profile_ele.find_element(
                        By.XPATH,
                        ".//div[@class='base-search-card__info']/h3[@class='base-search-card__title']",
                    ).text
                )
                try:
                    profile_subtitle = str(
                        profile_ele.find_element(
                            By.XPATH,
                            ".//div[@class='base-search-card__info']/h4[@class='base-search-card__subtitle']",
                        ).text
                    )
                except NoSuchElementException:
                    profile_subtitle = None

                try:
                    profile_metadata = str(
                        profile_ele.find_element(
                            By.XPATH,
                            ".//div[@class='base-search-card__info']/div[@class='base-search-card__metadata']",
                        ).text
                    )
                except NoSuchElementException:
                    profile_metadata = None
                # print(profile_title, profile_metadata)
                profile_data.append(
                    [
                        profile_title,
                        profile_link,
                        profile_subtitle,
                        profile_metadata,
                        None,
                    ]
                )
            # print(profile_data)
            print("Scraped all results.")
            save_to_csv(profile_data)
            print("Saved to csv.")
        else:
            results = []
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                results = soup.find_all(
                    "li", class_="reusable-search__result-container"
                )
            except Exception as e:
                print(e)
                print("Error searching main container.")
            print("Results found: ", len(results))
            if len(results) == 0:
                return False
            for li in results:
                ele = li.find("div", class_="mb1", recursive=True)
                if ele:
                    ele1 = ele.find("a", recursive=True)
                    if ele1:
                        profile_title = str(ele1.find(
                            "span",
                            attrs={"aria-hidden": "true"},
                            recursive=True,
                        ).get_text()).strip().replace("<!-- -->", "")
                        profile_link = ele1["href"]
                        profile_subtitle = str(ele.find(
                            "div",
                            class_="entity-result__primary-subtitle t-14 t-black t-normal",
                        ).text).strip().replace("<!-- -->", "")
                        profile_location = str(ele.find(
                            "div",
                            class_="entity-result__secondary-subtitle t-14 t-normal",
                        ).text).strip().replace("<!-- -->", "")
                    else:
                        profile_title = None
                        profile_link = None
                        profile_subtitle = None
                        profile_location = None
                profile_data.append(
                    [
                        profile_title,
                        profile_link,
                        profile_subtitle,
                        None,
                        profile_location,
                    ]
                )

            # print(profile_data)
            print("Scraped all results.")
            save_to_csv(profile_data)
            print("Saved to csv.")
    except Exception as e:
        print(e)
        if driver:
            driver.close()
            driver.quit()
    time.sleep(30)
    if driver:
        driver.close()
        driver.quit()


if __name__ == "__main__":
    main()
