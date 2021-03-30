from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from requests import get
import bs4
import os


rotten_tomatoes_url = "https://www.rottentomatoes.com"


def scrape_rotten_tomatoes(rt_url):
    options = webdriver.ChromeOptions()
    prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
                'permissions.default.stylesheet':2,
                'javascript': 2
            }
    }

    options.add_experimental_option("prefs", prefs)
    options.add_argument('headless')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
    driver.get(rt_url)

    try:
        print(driver.find_elements_by_xpath("//*[contains(text(), '404 - Not Found')]"))
        driver.close()
        return "404"
    except:
        pass


    element1 = WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.TAG_NAME, "score-board")))

    shadowRoot1 = driver.execute_script("return arguments[0].shadowRoot", element1)

    element_critic = shadowRoot1.find_element_by_tag_name("score-icon-critic")
    element_audience = shadowRoot1.find_element_by_tag_name("score-icon-audience")

    shadowRoot_critic = driver.execute_script("return arguments[0].shadowRoot", element_critic)
    shadowRoot_audience = driver.execute_script("return arguments[0].shadowRoot", element_audience)

    critic_score = shadowRoot_critic.find_elements_by_tag_name("span")[1].text
    audience_score = shadowRoot_audience.find_elements_by_tag_name("span")[1].text

    critic_icon = shadowRoot_critic.find_elements_by_tag_name("span")[0].get_attribute("class")

    driver.close()

    if "certified_fresh" in critic_icon:
        critic_icon = rotten_tomatoes_url + "/assets/pizza-pie/images/icons/tomatometer/certified_fresh.75211285dbb.svg"
    elif "fresh" in critic_icon:
        critic_icon = rotten_tomatoes_url + "/assets/pizza-pie/images/icons/tomatometer/tomatometer-fresh.149b5e8adc3.svg"
    elif "rotten" in critic_icon:
        critic_icon = rotten_tomatoes_url + "/assets/pizza-pie/images/icons/tomatometer/tomatometer-rotten.f1ef4f02ce3.svg"
    else:
        critic_icon = None
    # return critic_score, audience_score, critic_icon


    return {"critic_score": critic_score, "audience_score": audience_score, "critic_icon": critic_icon}


def metacritic_scrape(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    response = get(url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    if soup.find_all("span", "error_code"):
        return "404"

    scores = []

    for item in soup.find_all("a", class_="metascore_anchor"):
        if "</span>" in str(item):
            scores.append(item.text.strip())

    return {"metascore": scores[0], "user_score": scores[1]}

