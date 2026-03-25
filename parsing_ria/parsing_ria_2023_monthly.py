from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
import requests
import pandas as pd
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel


def is_target_element_present(browser):
    """Проверка наличия целевого элемента (Январь 2020)"""
    try:
        target_element = browser.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[24]/nav/div')
        return target_element.text == "Январь 2020"
    except NoSuchElementException:
        return False


def extract_article_info(info):
    """Извлечение информации о статье"""
    article_date = info.find('div', class_='list-item__info-item')
    article_name = info.find('a', class_='list-item__title color-font-hover-only')
    article_link = info.find('a', class_='list-item__title color-font-hover-only')
    
    if article_date and article_name and article_link:
        return {
            'date': article_date.text.strip(),
            'name': article_name.text.strip(),
            'link': article_link.get('href')
        }
    return None


def setup_browser_and_search(company):
    """Настройка браузера и выполнение поиска"""
    browser = webdriver.Chrome()
    url = 'https://ria.ru/search'
    browser.get(url)
    sleep(2)
    
    # Ввод названия компании
    input_company = browser.find_element(By.TAG_NAME, 'input')
    input_company.send_keys(company)
    input_company.send_keys(Keys.ENTER)
    sleep(2)
    
    return browser


def select_date_range(browser, start_xpath, end_xpath):
    """Выбор диапазона дат"""
    # Открыть фильтр с выбором периода
    period_open = wait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]'))
    )
    period_open.click()
    sleep(2)
    
    # Открыть календарь
    calendar_open = wait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]'))
    )
    calendar_open.click()
    sleep(2)
    
    # Прокрутка до нужной даты
    while not is_target_element_present(browser):
        element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
        element_to_scroll.send_keys(Keys.HOME)
        sleep(1)
    sleep(2)
    
    # Выбор конечной даты
    date_to = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, start_xpath)))
    browser.execute_script("arguments[0].scrollIntoView(true);", date_to)
    sleep(1)
    browser.execute_script("arguments[0].click();", date_to)
    sleep(2)
    
    # Выбор начальной даты
    date_from = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, end_xpath)))
    browser.execute_script("arguments[0].scrollIntoView(true);", date_from)
    sleep(1)
    browser.execute_script("arguments[0].click();", date_from)
    sleep(2)


def expand_all_articles(browser):
    """Раскрыть все статьи"""
    try:
        more_info = wait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]'))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", more_info)
        sleep(1)
        browser.execute_script("arguments[0].click();", more_info)
        sleep(2)
    except Exception:
        print('Все статьи выведены на странице')


def scrape_articles_from_page(browser):
    """Сбор статей с текущей страницы"""
    soup = BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_='list-item')
    
    articles = []
    for info in search_results:
        article_info = extract_article_info(info)
        if article_info:
            articles.append(article_info)
    
    return articles


def get_article_text(articles):
    """Получение текста статей по ссылкам"""
    for article in articles:
        url = article['link']
        try:
            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                article_content = soup.find_all(class_=['article__text', 'article__quote-text'])
                if article_content:
                    combined_text = ''.join([element.text.strip() for element in article_content])
                    article['article'] = combined_text
                sleep(5)
            else:
                print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
        except Exception as e:
            print(f"Произошла ошибка при обработке ссылки {url}: {e}")
    
    return articles


def remove_duplicates(articles):
    """Удаление дубликатов по ссылкам"""
    unique_articles = {}
    for article in articles:
        unique_articles.setdefault(article['link'], article)
    return list(unique_articles.values())


def process_month(browser, company, start_xpath, end_xpath, all_articles):
    """Обработка одного месяца"""
    browser = setup_browser_and_search(company)
    
    # Выбор диапазона дат
    select_date_range(browser, start_xpath, end_xpath)
    
    # Раскрыть все статьи
    expand_all_articles(browser)
    
    # Сбор статей
    articles = scrape_articles_from_page(browser)
    browser.quit()
    
    # Добавление в общий список
    all_articles.extend(articles)
    
    return all_articles


# Основная программа
company = 'компания ВК'
all_articles_2023 = []

# XPath для каждого месяца (начальная и конечная даты)
months_config = [
    # Январь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[60]/div/div[7]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[60]/div/div[37]'),
    # Февраль 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[61]/div/div[3]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[61]/div/div[30]'),
    # Март 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[62]/div/div[3]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[62]/div/div[33]'),
    # Апрель 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[63]/div/div[6]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[63]/div/div[35]'),
    # Май 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[64]/div/div[1]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[64]/div/div[31]'),
    # Июнь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[65]/div/div[4]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[65]/div/div[33]'),
    # Июль 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[66]/div/div[6]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[66]/div/div[36]'),
    # Август 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[67]/div/div[2]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[67]/div/div[32]'),
    # Сентябрь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[68]/div/div[5]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[68]/div/div[34]'),
    # Октябрь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[69]/div/div[7]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[69]/div/div[37]'),
    # Ноябрь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[70]/div/div[3]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[70]/div/div[32]'),
    # Декабрь 2023
    ('//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[71]/div/div[5]',
     '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[71]/div/div[35]')
]

# Сбор статей за все месяцы
for start_xpath, end_xpath in months_config:
    browser = None
    try:
        all_articles_2023 = process_month(browser, company, start_xpath, end_xpath, all_articles_2023)
    except Exception as e:
        print(f"Ошибка при обработке месяца: {e}")
        if browser:
            browser.quit()

# Удаление дубликатов
all_articles_2023 = remove_duplicates(all_articles_2023)

# Получение текста статей
all_articles_2023 = get_article_text(all_articles_2023)

print(f"Количество скачанных статей за 2023 год: {len(all_articles_2023)}")

# Анализ тональности
df_2023 = pd.DataFrame(all_articles_2023)
print(df_2023.head())

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)
df_2023['article_sentiment'] = model.predict(df_2023['article'], k=5)

sentiment = pd.json_normalize(df_2023['article_sentiment'])
sentiment = sentiment.mean().round(4)

print(f"Neutral 2023: {sentiment['neutral']}")
print(f"Negative 2023: {sentiment['negative']}")
print(f"Positive 2023: {sentiment['positive']}")
print(f"Speech 2023: {sentiment['speech']}")
print(f"Skip 2023: {sentiment['skip']}")
