import asyncio
import datetime
import aiofiles
from alkoChecker import *
from aiocsv import AsyncWriter
from selenium import webdriver
import time

from bs4 import BeautifulSoup

cities = {
    '1': 'Москва',
    '2': 'Санкт-Петербург',
    '3': 'Челябинск',
    '4': 'Новосибирск',
    '5': 'Краснодар',
}
cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')


async def entry(city_path='2', age=20, quantity=250):
    driver = webdriver.Chrome(
        executable_path='C:\\Users\\anato\\PycharmProjects\\tgMagnit\\chromedriver.exe',
    )

    driver.get('https://magnit.ru/promo/')
    time.sleep(1)

    close_button = driver.find_element('xpath', '/html/body/div[10]/div/div[1]/div[1]')
    close_button.click()
    time.sleep(1)
    # закрываю рекламу

    yes_button = driver.find_element('xpath', '/html/body/div[6]/div/div[1]/div[2]/div/div/button[2]')
    yes_button.click()
    time.sleep(1)
    # подтвержда, что есть 18

    city_button = driver.find_element('xpath', '/html/body/div[3]/header/div/div[1]/a[1]/span')
    city_button.click()
    time.sleep(1)
    # захожу в меню выбор города

    city_input = driver.find_element('name', 'citySearch')
    city_input.clear()
    city_input.click()
    city_input.send_keys('ы')  # иначе города не прогружаются
    time.sleep(1)

    city_chose = driver.find_element('xpath', f'//*[@id="mCSB_1_container"]/div[2]/div/div[{city_path}]/a')
    city_chose.click()
    time.sleep(4)
    # выбираю нужный город

    close_button = driver.find_element('xpath', '/html/body/div[10]/div/div[1]/div[1]')
    close_button.click()
    time.sleep(1)
    # закрываю рекламу

    hrefs = set()
    for i in range(int(quantity * 1.3) // 50 + 2):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        driver.execute_script('window.scrollBy(0, -1000);')
        time.sleep(0.5)
    # Скролим ленту
    for item in driver.find_elements('tag name', 'a'):
        if ('https://magnit.ru/promo/' in str(item.get_attribute('href'))) and (
                'https://magnit.ru/promo/' != str(item.get_attribute('href'))):
            hrefs.add(item.get_attribute('href'))
            if len(hrefs) > quantity:
                break
        print(len(hrefs))
    # Отбираем первые quantity продуктов
    hrefs = list(hrefs)[:quantity + 1]
    for i in hrefs:
        print(str(i))
    with open('index_selenium.html', 'w', encoding='utf16') as file:
        file.write(driver.page_source)
    # сохраняю html код
    driver.close()
    driver.quit()

    with open('index_selenium.html', encoding='utf16') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')

    cards = soup.find_all('a', class_='card-sale_catalogue')

    data = []
    i = 0
    for card in cards[:quantity + 1]:
        card_title = card.find('div', class_='card-sale__title').text.strip()
        try:
            card_discount = card.find('div', class_='card-sale__discount').text.strip()
        except AttributeError:
            continue

        card_price_old_integer = card.find('div', class_='label__price_old').find('span',
                                                                                  class_='label__price-integer').text.strip()
        card_price_old_decimal = card.find('div', class_='label__price_old').find('span',
                                                                                  class_='label__price-decimal').text.strip()
        card_old_price = f'{card_price_old_integer},{card_price_old_decimal}'

        card_price_integer = card.find('div', class_='label__price_new').find('span',
                                                                              class_='label__price-integer').text.strip()
        card_price_decimal = card.find('div', class_='label__price_new').find('span',
                                                                              class_='label__price-decimal').text.strip()
        card_price = f'{card_price_integer},{card_price_decimal}'

        card_sale_date = card.find('div', class_='card-sale__date').text.strip().replace('\n', ' ')

        try:
            data.append(
                [card_title, card_discount, card_old_price, card_price, card_sale_date, hrefs[i]]
            )
        except:
            pass
        i += 1
        # Достаем нужную информацию о продукте и собираем ее в массив data

    file_name = f'{cities.get(city_path)}_{cur_time}.csv'
    async with aiofiles.open(file_name, 'w', encoding='utf16', newline="") as file:
        writer = AsyncWriter(file, delimiter="\t")
        await writer.writerow(
            [
                'Продукт',
                'Процент скидки',
                'Старая цена',
                'Новая цена',
                'Время акции',
            ]
        )
        await writer.writerows(
            data
        )
        # Записываю data в csv файл
        if age < 18:
            delete_alko(file_name)
        # Удаление алкоголя в случае если возраст меньше 18

    return f'{cities.get(city_path)}_{cur_time}.csv'


async def main():
    await entry('5')


if __name__ == '__main__':
    asyncio.run(main())
# Если нужно то можно проверять парсер независимо от бота
