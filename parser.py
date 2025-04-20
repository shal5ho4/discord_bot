import http
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# from logger import logger

# config
# LAST_SEEN_TITLE = 'last_seen_title.txt'
# LAST_SEEN_TITLE = '/tmp/last_seen_title.txt'      # for Lambda

WEEKLY_UPDATE_KWORD = '週アップデートまとめ'
BOOSTED_JOB_TITLE = '報酬アップ'

# def get_previous_title() -> str:
#     if not os.path.exists(LAST_SEEN_TITLE):
#         return ""

#     with open(LAST_SEEN_TITLE, encoding='utf-8') as f:
#         title = f.read()
#         print(f'previous article title: "{title}"')
#     return title


# def set_new_title(title: str):
#     with open(LAST_SEEN_TITLE, 'w', encoding='utf-8') as f:
#         f.write(title)


class Parser:
    def __init__(self, url: str):
        self.url: str = url
        self.parser: BeautifulSoup = None
        self.get_http()

    def get_http(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(self.url, headers=headers)

        if response.status_code != http.HTTPStatus.OK:
            print(f'get_http: request failed with status code "{response.status_code}"')
            raise Exception(f'request failed with status code {response.status_code}')
        
        self.parser = BeautifulSoup(response.content, 'html.parser')
    

class ArticleListParser(Parser):
    def __init__(self, url):
        super().__init__(url)
        self._title = None
        self._link = None

    @property
    def title(self):
        if not self._title:
            self.get_new_article()
        return self._title
    
    @property
    def link(self):
        if not self._link:
            self.get_new_article()
        return self._link

    def get_new_article(self):
        articles = self.parser.find_all('h2', class_='entry_title')

        for article in articles:
            title = article.text.strip()

            if WEEKLY_UPDATE_KWORD in title and article.a:
                self._title = article.text.strip()
                self._link = article.a['href']
                break


class ArticleParser(Parser):
    def get_notification_message(self) -> str:
        date = self._get_date_from_url()
        
        topics = self._get_article_topics()
        topic_lines = '\n'.join([f"●{topic}" for topic in topics])

        boosted_jobs = self._get_boosted_jobs()
        boosted_job_lines = '\n'.join([f"・{job}" for job in boosted_jobs])

        message = f"""🎈 {date}
🆕今週の週アップデート速報🆕
{topic_lines}

💲報酬アップ
{boosted_job_lines}

⬇️詳しくはこちら⬇️
{self.url}"""
        
        print(message)

        return message

    def _get_date_from_url(self) -> str | None:
        match = re.search(r'weekly(\d{8})', self.url)
        if not match:
            return None
        
        date_str = match.group(1)   # "20250313"
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        day_of_week = '月火水木金土日'
        index = date_obj.weekday()

        formatted = f'{date_obj.strftime("%Y/%m/%d")}({day_of_week[index]})'    # "2025/03/13(木)"

        return formatted
    
    def _get_article_topics(self) -> list[str] | None:
        ul = self.parser.find('ul', class_='b weekly')
        if not ul:
            return None
        
        topics = [li.get_text(strip=True) for li in ul.find_all('li')]

        return topics
    
    def _get_boosted_jobs(self) -> list[str] | None:
        h2 = self.parser.find('h2', string=BOOSTED_JOB_TITLE)
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


if __name__ == '__main__':
    from settings import WEEKLY_URL
    list_parser = ArticleListParser(WEEKLY_URL)

    print(f'parser.title = {list_parser.title}')
    print(f'parser.link = {list_parser.link}')

    article_parser = ArticleParser(list_parser.link)
    message = article_parser.get_notification_message()
