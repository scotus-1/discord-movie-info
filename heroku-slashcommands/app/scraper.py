from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import lxml.html
import cchardet
import traceback
import bs4



def scrape_rotten_tomatoes(rt_url, request_session, driver):
    try:
        response = request_session.get(rt_url, stream=True)
        response.raw.decode_content = True
        tree = lxml.html.parse(response.raw)

        print(tree.xpath("//*[contains(text(), '404 - Not Found')]"))
        return "404"
    except:
        traceback.print_exc()

    driver.get(rt_url)

    try:
        element1 = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, "score-board")))

        shadowRoot1 = driver.execute_script("return arguments[0].shadowRoot", element1)

        element_critic = shadowRoot1.find_element_by_tag_name("score-icon-critic")
        element_audience = shadowRoot1.find_element_by_tag_name("score-icon-audience")

        shadowRoot_critic = driver.execute_script("return arguments[0].shadowRoot", element_critic)
        shadowRoot_audience = driver.execute_script("return arguments[0].shadowRoot", element_audience)

        critic_score = shadowRoot_critic.find_elements_by_tag_name("span")[1].text
        audience_score = shadowRoot_audience.find_elements_by_tag_name("span")[1].text



        return {"critic_score": critic_score, "audience_score": audience_score}
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

