import playwright
from playwright.sync_api import Page, expect, sync_playwright
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import requests
import json

## Блок №1: получение данных о пути туда
# 1. задание вводных данных
x = 'Amsterdam'  # город нахождения пользователя
date_start = 'January 30, 2024'  # дата старта поездки пользователя
date_back = 'January 31, 2024'  # дата окончания поездки пользователя (возврат обратно в город нахождения)
y = ['Utrecht']  # потенциальные города для визита   ['Rotterdam', 'Dortmund', 'Berlin']

key_tr = '504C4C443DF8452183B91AE58961F70D'

p = sync_playwright().start()
browser = p.firefox.launch() #(headless=False) #, slow_mo=10)  # chromium
page = browser.new_page()

# 2. запуск браузера и получение информации по жд билетам из текущего места нахождения пользователя
lst_trains_start = []
for i in range(len(y)):

    # 2.1. ввод городов маршрута
    page.goto("https://saveatrain.com")
    search_from = page.locator('input[placeholder="From"]')
    search_from.click()
    search_from.clear()
    search_from.type(x)
    #search_from.press("Enter")
    search_to = page.locator('input[placeholder="To"]')
    search_to.click()
    search_to.clear()
    search_to.type(y[i])
    #search_to.press("Enter")
    page.get_by_role("button", name="Search").click()

    # 2.2. ввод даты отправления
    page.wait_for_load_state('load')
    date = page.locator('input[id="main-form-departure-date"]')
    date.click()
    txt_date2 = 'td[aria-label="' + date_start + '"]'
    date2 = page.locator(txt_date2)
    date2.click()


    button = page.get_by_role("button", name="Find my tickets")
    button.wait_for(state='attached', timeout=3000) #1000 - 1 секунда
    button.click()

    # 4.
    page.is_visible('div.results-container')

    col_names = ['departure_city', 'destination_city', 'price', 'departure_day', 'departure_time', 'arrival_day', 'arrival_time']
    destination_city = y[i]
    departure_city = x

    # цикл для того, чтобы выдернуть все нужные нам параметры маршрута
    table = PrettyTable()
    table.field_names = col_names
    for i in range(1, 4):
        dics_details = {}
        lst_row = []
        lst_row.append(departure_city)
        dics_details['departure_city'] = departure_city
        lst_row.append(destination_city)
        dics_details['destination_city'] = destination_city
        html_ind = '#result-' + str(i)
        html = page.inner_html(html_ind)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.find_all('div'))
        price_ind = 'price-' + str(i)
        price = soup.find('p', {'id': price_ind}).text
        dep_d_ind = 'departure-d-' + str(i)
        dep_d = soup.find('p', {'id': dep_d_ind}).text
        dep_t_ind = 'departure-t-' + str(i)
        dep_t = soup.find('p', {'id': dep_t_ind}).text
        arr_d_ind = 'arrival-d-' + str(i)
        arr_d = soup.find('p', {'id': arr_d_ind}).text
        arr_t_ind = 'arrival-t-' + str(i)
        arr_t = soup.find('p', {'id': arr_t_ind}).text
        lst_row.append(price)
        dics_details['price'] = price
        lst_row.append(dep_d)
        dics_details['departure_day'] =dep_d
        lst_row.append(dep_t)
        dics_details['departure_time'] =dep_t
        lst_row.append(arr_d)
        dics_details['arrival_day'] = arr_d
        lst_row.append(arr_t)
        dics_details['arrival_time'] = arr_t
        table.add_row(lst_row)
        lst_trains_start.append(dics_details)

        # 6. рисуем в терминале табличку
    table.border = True
    table.header = True
    table.padding_width = 1

    print(table)

#browser.close()

#print(lst_trains_start)

#######################################################################################################################
## Блок №2: получение данных о пути обратно

# 2. запуск браузера и получение информации по жд билетам из места путешествия в изначальную точку
lst_trains_back = []
for i in range(len(y)):

    # 2.1. ввод городов маршрута
    page.goto("https://saveatrain.com")
    search_from = page.locator('input[placeholder="From"]')
    search_from.click()
    search_from.clear()
    search_from.type(y[i])
    search_from.press("Enter")
    search_to = page.locator('input[placeholder="To"]')
    search_to.click()
    search_to.clear()
    search_to.type(x)
    search_to.press("Enter")
    page.get_by_role("button", name="Search").click()

    # 2.2. ввод даты отправления
    page.wait_for_load_state('load')
    date = page.locator('input[id="main-form-departure-date"]')
    date.click()
    txt_date2 = 'td[aria-label="' + date_back + '"]'
    date2 = page.locator(txt_date2)
    date2.click()
    date2.press("Enter")

    page.is_visible('div.booking-content tickets-search ng-star-inserted')
    page.get_by_role("button", name="Find my tickets").click()

    # 4.
    page.is_visible('div.results-container')

    col_names = ['departure_city', 'destination_city', 'price', 'departure_day', 'departure_time', 'arrival_day', 'arrival_time']
    departure_city = y[i]
    destination_city = x

    # цикл для того, чтобы выдернуть все нужные нам параметры маршрута
    table = PrettyTable()
    table.field_names = col_names
    for i in range(1, 4):
        dics_details = {}
        lst_row = []
        lst_row.append(departure_city)
        dics_details['departure_city'] = departure_city
        lst_row.append(destination_city)
        dics_details['destination_city'] = destination_city
        html_ind = '#result-' + str(i)
        html = page.inner_html(html_ind)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.find_all('div'))
        price_ind = 'price-' + str(i)
        price = soup.find('p', {'id': price_ind}).text
        dep_d_ind = 'departure-d-' + str(i)
        dep_d = soup.find('p', {'id': dep_d_ind}).text
        dep_t_ind = 'departure-t-' + str(i)
        dep_t = soup.find('p', {'id': dep_t_ind}).text
        arr_d_ind = 'arrival-d-' + str(i)
        arr_d = soup.find('p', {'id': arr_d_ind}).text
        arr_t_ind = 'arrival-t-' + str(i)
        arr_t = soup.find('p', {'id': arr_t_ind}).text
        lst_row.append(price)
        dics_details['price'] = price
        lst_row.append(dep_d)
        dics_details['departure_day'] =dep_d
        lst_row.append(dep_t)
        dics_details['departure_time'] =dep_t
        lst_row.append(arr_d)
        dics_details['arrival_day'] = arr_d
        lst_row.append(arr_t)
        dics_details['arrival_time'] = arr_t
        table.add_row(lst_row)
        lst_trains_back.append(dics_details)

        # 6. рисуем в терминале табличку
    table.border = True
    table.header = True
    table.padding_width = 1

    print(table)

browser.close()

#print(lst_trains_back)

#######################################################################################################################
## Блок №3: получение данных о точках интереса внутри городов
#1. задаём город, который будет приходить из предыдущего этапа и ключ партнёра tripadvisor
for i in range(len(y)):
    city = y[i]


    #2. задаём url и получаем результат вызова 10 точек интереса для заданного города (трипадвизор выдаёт максимум 10 шт)
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key_tr}&searchQuery={city}&category=attractions&address={city}&language=en"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)

    #3. создаём из строки со всеми данными лист с id точек интереса, по которому будем итерироваться при поиске деталей
    lst=[]
    for j in range(10):
        lst.append(json.loads(response.text)['data'][j]['location_id'])

    #4. создаём справочные списки: с интересующими параметрами и с ключами итогового словаря
    parameters = ["['name']", "['address_obj']['address_string']", "['ranking_data']['ranking_string']"
                ,"['rating']","['groups'][0]['categories'][0]['name']"]
    col_names = ['name', 'address', 'ranking', 'rating', 'subcategory']

    #5. вызываем location details реквест для получения нужных параметров и готовим данные для отрисовки в терминале
    lst_objects = []
    x = PrettyTable()
    x.field_names = col_names
    for j in range(len(lst)): # это объекты
        url = f"https://api.content.tripadvisor.com/api/v1/location/{lst[j]}/details?key={key_tr}&language=en&currency=USD"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        dics_details={}
        lst_row=[]
        for k in range(len(parameters)):
            info = f'json.loads(response.text){parameters[k]}'
            key = col_names[k]
            try:
                dics_details[key] = eval(info)
                lst_row.append(eval(info))
            except Exception:
                dics_details[key] = ''
                lst_row.append('')
        lst_objects.append(dics_details)
        x.add_row(lst_row)

    # print(lst_objects)

    #6. рисуем в терминале табличку
    x.border = True
    x.header = True
    x.padding_width = 1

    print(x)