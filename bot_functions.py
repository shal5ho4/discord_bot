import http
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from logger import logger

# config
URL = 'https://gta5-madara.com/category/weeklyupdate/'
LAST_SEEN_TITLE = 'last_seen_title.txt'

WEEKLY_UPDATE_KWORD = '週アップデートまとめ'
BOOSTED_JOB_TITLE = '報酬アップ'


def get_http(url: str) -> requests.Response | None:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f'request failed with status code "{response.status_code}"')
        raise Exception(f'request failed with status code {response.status_code}')

    return response


def get_previous_title() -> str:
    with open(LAST_SEEN_TITLE, encoding='utf-8') as f:
        title = f.read()
        logger.info(f'previous article title: "{title}"')
    return title


def set_new_title(title: str):
    with open(LAST_SEEN_TITLE, 'w', encoding='utf-8') as f:
        f.write(title)


def get_article_title_and_link() -> tuple[str, str] | tuple[None, None]:
    response = get_http(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('h2', class_='entry_title')

    for article in articles:
        title = article.text.strip()
        if WEEKLY_UPDATE_KWORD in title and article.a:
            title = article.text.strip()
            link = article.a['href']
            logger.info(f'new article title: "{title}"')
            return title, link
    
    logger.error('new article not found')
    return None, None


def get_date_from_url(article_url: str) -> str | None:
    match = re.search(r'weekly(\d{8})', article_url)
    if not match:
        return None
    
    date_str = match.group(1)  # e.g., "20250313"

    date_obj = datetime.strptime(date_str, "%Y%m%d")
    day_of_week = '月火水木金土日'
    index = date_obj.weekday()

    formatted = f'{date_obj.strftime("%Y/%m/%d")}({day_of_week[index]})'  # e.g., "2025/03/13(木)"

    return formatted


def get_article_topics(article_url: str) -> list[str] | None:
    response = get_http(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    ul = soup.find('ul', class_='b weekly')
    if not ul:
        return None

    topics = [li.get_text(strip=True) for li in ul.find_all('li')]

    return topics


def get_boosted_jobs(article_url: str) -> list[str] | None:
    response = get_http(article_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    h2 = soup.find('h2', string=BOOSTED_JOB_TITLE)
    if not h2:
        return None
    
    p = h2.find_next_sibling('p')
    if not p:
        return None
    
    boosted_jobs = []
    current_line = ''

    for elem in p.children:
        if elem.name == 'br':
            if current_line.strip():
                boosted_jobs.append(current_line.strip())
            current_line = ""
        elif elem.name == 'span':
            current_line += f"  {elem.get_text()}"
        elif isinstance(elem, str):
            current_line += elem.strip()
    
    if current_line.strip():
        boosted_jobs.append(current_line.strip())

    return boosted_jobs


def get_notification_message() -> str:
    previous_title = get_previous_title()
    new_title, new_link = get_article_title_and_link()

    if previous_title != new_title:
        set_new_title(new_title)
        logger.info(f'successfully updated "{LAST_SEEN_TITLE}".')

    date = get_date_from_url(new_link)

    topics = get_article_topics(new_link)
    topic_lines = "\n".join([f"●{topic}" for topic in topics])

    boosted_jobs = get_boosted_jobs(new_link)
    boosted_job_lines = "\n".join([f"・{job}" for job in boosted_jobs])

    message = f"""🎈 {date}
🆕今週の週アップデート速報🆕
{topic_lines}

💲報酬アップ
{boosted_job_lines}

⬇️詳しくはこちら⬇️
{new_link}"""
    print(message)

    return message


def send_discord_webhook(message: str, webhook_url: str):
    headers = {'Content-Type': 'application/json'}
    data = {'content': message}
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

    if response.status_code != 204:
        logger.error(f"Webhook failed with status code {response.status_code}")


if __name__ == '__main__':
    get_notification_message()
