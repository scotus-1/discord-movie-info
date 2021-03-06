from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from app.globals import discord_endpoint, auth_headers
from selenium import webdriver
import lxml.html
import cchardet
import traceback
import bs4
import os


def create_driver():
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'permissions.default.stylesheet': 2,
            'javascript': 2
        }
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('headless')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    return webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)


def scrape_rotten_tomatoes(media_type, rt_url, request_session, **kwargs):
    try:
        response = request_session.get(rt_url, stream=True)
        response.raw.decode_content = True
        tree = lxml.html.parse(response.raw)
        if tree.xpath("//*[contains(text(), '404 - Not Found')]"):
            return "404"

        driver = kwargs['driver']
        if media_type == "movie":
            driver.get(rt_url)
            element1 = WebDriverWait(driver, 60).until(ec.presence_of_element_located((By.TAG_NAME, "score-board")))

            shadowRoot1 = driver.execute_script("return arguments[0].shadowRoot", element1)

            element_critic = shadowRoot1.find_element_by_tag_name("score-icon-critic")
            element_audience = shadowRoot1.find_element_by_tag_name("score-icon-audience")

            shadowRoot_critic = driver.execute_script("return arguments[0].shadowRoot", element_critic)
            shadowRoot_audience = driver.execute_script("return arguments[0].shadowRoot", element_audience)

            critic_score = shadowRoot_critic.find_elements_by_tag_name("span")[1].text
            audience_score = shadowRoot_audience.find_elements_by_tag_name("span")[1].text
        elif media_type == "tv":
            response = request_session.get(rt_url, stream=True)
            response.raw.decode_content = True
            tree = lxml.html.parse(response.raw)

            try:
                print(tree.xpath("//*[@id='tomato_meter_link']/span/span[2]")[0].text_content().strip())
                print(tree.xpath("//*[@id='topSection']/section/div[1]/section/section/div[2]/h2/a/span/span[2]")[0].text_content().strip())
            except:
                traceback.print_exc()

            try:
                critic_score = tree.xpath("//*[@id='tomato_meter_link']/span/span[2]")[0].text_content().strip()
            except:
                traceback.print_exc()
                critic_score = "N/A"

            try:
                audience_score = tree.xpath("//*[@id='topSection']/section/div[1]/section/section/div[2]/h2/a/span/span[2]")[0].text_content().strip()
            except:
                traceback.print_exc()
                audience_score= "N/A"
        else:
            critic_score = "N/A"
            audience_score = "N/A"


        return {"critic_score": critic_score, "audience_score": audience_score}
    except TimeoutError:
        traceback.print_exc()
        return {"critic_score": "N/A", "audience_score": "408 Timeout"}
    except:
        traceback.print_exc()
        return {"critic_score": "N/A", "audience_score": "N/A"}


def metacritic_scrape(url, request_session):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

        response = request_session.get(url, headers=headers)
        soup = bs4.BeautifulSoup(response.content, 'lxml')

        if soup.find_all("span", "error_code"):
            return "404"

        scores = []

        for item in soup.find_all("a", class_="metascore_anchor"):
            if "</span>" in str(item):
                scores.append(item.text.strip())

        return {"metascore": scores[0], "user_score": scores[1]}
    except:
        traceback.print_exc()
        return {"metascore": "--", "user_score": "--"}


def rotten_tomatoes_handler(media_type, title, title_year, embed, app_id, interaction_token, session):

    discord_url = discord_endpoint + f"/webhooks/{app_id}/{interaction_token}/messages/@original"
    base_url = ""
    driver = None
    if media_type == "tv":
        base_url = "https://rottentomatoes.com/tv/"
    elif media_type == "movie":
        base_url = "https://rottentomatoes.com/m/"
        driver = create_driver()


    if "the" in title.split(" ")[0]:
        words = title_year.split(" ")
        words.pop(0)
        words = " ".join(words)

        word = title.split(" ")
        word.pop(0)
        word = " ".join(word)


        rotten_tomatoes_url = base_url + words.replace(" ", "_")
        rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
        print(rotten_tomatoes_url)
        if rt_value == "404":
            rotten_tomatoes_url = base_url + title_year.replace(" ", "_")
            rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
            print(rotten_tomatoes_url)
            if rt_value == "404":
                rotten_tomatoes_url = base_url + word.replace(" ", "_")
                rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
                print(rotten_tomatoes_url)
                if rt_value == "404":
                    rotten_tomatoes_url = base_url + title.replace(" ", "_")
                    rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
                    print(rotten_tomatoes_url)
                    if rt_value == "404":
                        rt_value = {"critic_score": "N/A", "audience_score": "N/A"}
    else:
        rotten_tomatoes_url = base_url + title_year.replace(" ", "_")
        rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
        if rt_value == "404":
            rotten_tomatoes_url = base_url + title.replace(" ", "_")
            rt_value = scrape_rotten_tomatoes(media_type, rotten_tomatoes_url, session, driver=driver)
            if rt_value == "404":
                rt_value = {"critic_score": "N/A", "audience_score": "N/A"}

    if driver:
        driver.close()
    embed['fields'][7]['value'] = f"[{rt_value['critic_score']} | {rt_value['audience_score']}]({rotten_tomatoes_url}) (Critic | Audience)"

    return session.patch(discord_url, headers=auth_headers, json={"embeds": [embed]}).text
