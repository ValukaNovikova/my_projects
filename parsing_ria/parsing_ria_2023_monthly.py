from selenium import webdriver # Для работы с веб-драйверами браузеров
from selenium.webdriver import Chrome # Конкретный драйвер для браузера Chrome
from selenium.webdriver.chrome.options import Options # Для настройки параметров запуска Chrome (например, режим инкогнито)
from selenium.webdriver.common.by import By # Для использования различных стратений поиска элементов на странице
from selenium.webdriver.common.keys import Keys # Импорт констант клавиш клавиатуры для симуляции нажатия кнопок (например, Enter)
from selenium.webdriver.support.ui import WebDriverWait as wait # Для ожидания загрузки определенных элементов страницы
from selenium.webdriver.support import expected_conditions as EC # Импорт различных условий ожидания, такие как наличие элемента на странице
from selenium.common.exceptions import NoSuchElementException # Для обработки случаев отсутствия искомого элемента
from bs4 import BeautifulSoup # Для парсинга HTML-кода страниц
from time import sleep # Для добавления паузы между действиями
import requests # Для загрузки страницы
import pandas as pd 
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

# Функция для проверки наличия нужного элемента
def is_target_element_present():
    try:
        target_element = browser.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[24]/nav/div')
        return target_element.text == "Январь 2020"
    except NoSuchElementException:
        return False

# Функция для сбора данных по выведенным статиям
def extract_article_info(info):
    article_date = info.find('div', class_='list-item__info-item')
    article_name = info.find('a', class_='list-item__title color-font-hover-only')
    article_link = info.find('a', class_='list-item__title color-font-hover-only')
    if article_date and article_name and article_link:
        date_text = article_date.text.strip()
        name_text = article_name.text.strip()
        link_href = article_link.get('href')
        return {
            'date': date_text,
            'name': name_text,
            'link': link_href
        }
    else:
        return None

company = 'компания ВК'
df_2023 = []

# Январь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_1 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[60]/div/div[7]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_1)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_1)
sleep(2)
date_from_2023_1 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[60]/div/div[37]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_1)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_1)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Февраль 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_2 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[61]/div/div[3]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_2)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_2)
sleep(2)
date_from_2023_2 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[61]/div/div[30]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_2)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_2)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Март 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_3 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[62]/div/div[3]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_3)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_3)
sleep(2)
date_from_2023_3 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[62]/div/div[33]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_3)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_3)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Апрель 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_4 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[63]/div/div[6]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_4)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_4)
sleep(2)
date_from_2023_4 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[63]/div/div[35]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_4)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_4)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Май 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_5 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[64]/div/div[1]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_5)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_5)
sleep(2)
date_from_2023_5 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[64]/div/div[31]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_5)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_5)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Июнь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_6 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[65]/div/div[4]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_6)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_6)
sleep(2)
date_from_2023_6 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[65]/div/div[33]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_6)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_6)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Июль 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_7 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[66]/div/div[6]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_7)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_7)
sleep(2)
date_from_2023_7 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[66]/div/div[36]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_7)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_7)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Август 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_8 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[67]/div/div[2]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_8)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_8)
sleep(2)
date_from_2023_8 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[67]/div/div[32]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_8)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_8)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Сентябрь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_9 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[68]/div/div[5]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_9)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_9)
sleep(2)
date_from_2023_9 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[68]/div/div[34]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_9)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_9)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Октябрь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_10 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[69]/div/div[7]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_10)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_10)
sleep(2)
date_from_2023_10 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[69]/div/div[37]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_10)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_10)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Ноябрь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_11 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[70]/div/div[3]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_11)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_11)
sleep(2)
date_from_2023_11 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[70]/div/div[32]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_11)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_11)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()

# Декабрь 2023 года
browser = webdriver.Chrome()
url = 'https://ria.ru/search'
browser.get(url)
sleep(2)
# Ввести наименование компании
input_company = browser.find_element(By.TAG_NAME, 'input')
input_company.send_keys(f"{company}")
input_company.send_keys(Keys.ENTER)
sleep(2)
# Открыть фильтр с выбором периода
period_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="search-panel__filter"][data-param="interval"]')))
period_open.click()
sleep(2)
# Открыть календарь для выбора периода
calendar_open = wait(browser, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-open="calendar"]')))
calendar_open.click()
sleep(2)
# Цикл для выполнения действия
while not is_target_element_present():
    element_to_scroll = browser.find_element(By.CSS_SELECTOR, 'div[class="the-in-scroll__box"]')
    element_to_scroll.send_keys(Keys.HOME)
    sleep(1)
sleep(2)
# Выбор периода
date_to_2023_12 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[71]/div/div[5]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_to_2023_12)
sleep(1)
browser.execute_script("arguments[0].click();", date_to_2023_12)
sleep(2)
date_from_2023_12 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div[71]/div/div[35]')))
browser.execute_script("arguments[0].scrollIntoView(true);", date_from_2023_12)
sleep(1)
browser.execute_script("arguments[0].click();", date_from_2023_12)
sleep(2)
# Раскрыть все статьи по году
try:
    more_info_2023 = wait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[1]/div/div/div[3]')))
    browser.execute_script("arguments[0].scrollIntoView(true);", more_info_2023)
    sleep(1)
    browser.execute_script("arguments[0].click();", more_info_2023)
    sleep(2)
except Exception as e:
        print('Все статьи выведены на странице')
# Запись в словарь данных по выведенным статьям
while True:
    soup =  BeautifulSoup(browser.page_source, 'lxml')
    search_results = soup.find_all('div', class_ = 'list-item')
    for info in search_results:
        article_info_2023 = extract_article_info(info)
        if article_info_2023:
            df_2023.append(article_info_2023)
    break
# Создаем новый словарь, где ключи — уникальные ссылки, а значения — соответствующие записи
unique_articles = {}
for article in df_2023:
    unique_articles.setdefault(article['link'], article)
df_2023 = list(unique_articles.values()) # Преобразуем обратно в список значений
# Достаем текст по каждой статье по ссылке и добавляем в df_2023
for articles in df_2023:
    url = articles['link'] # Извлекаем ссылку из текущего элемента
    try:
        response = requests.get(url) # Получаем HTML-код страницы
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            article = soup.find_all(class_=['article__text', 'article__quote-text'])
            if article is not None:
                combined_text = ''.join([element.text.strip() for element in article])
                articles['article'] = combined_text
            sleep(5)
        else:
            print(f"Запрос вернул статус-код {response.status_code}, ссылка: {url}")
    except Exception as e:
        print(f"Произошла ошибка при обработке ссылки {url}: {e}")
browser.quit()


print(f"Количество скачанных статей за 2023 год: {len(df_2023)}")

# Анализ тональности
df_2023 = pd.DataFrame(df_2023)
# print(df_2023.head())
tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer = tokenizer)
df_2023['article_sentiment'] = model.predict(df_2023['article'], k = 5)
# print(df_2023['article_sentiment'].head().to_string(index = False))
sentiment = pd.json_normalize(df_2023['article_sentiment']) # Разделяем столбец article_sentiment на отдельные столбцы по ключам
sentiment = sentiment.mean().round(4)
print(f"Neutral 2023: {sentiment['neutral']}")
print(f"Negative 2023: {sentiment['negative']}")
print(f"Positive 2023: {sentiment['positive']}")
print(f"Speech 2023: {sentiment['speech']}")
print(f"Skip 2023: {sentiment['skip']}")