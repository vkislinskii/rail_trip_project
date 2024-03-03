#from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    if request.method == "GET":
        return first_page(request)
    else:
        return processing_page(request)

def first_page(request):
    from datetime import datetime
    from core.models import Cities

    today = datetime.today().strftime('%Y-%m-%d')
    all_cities = Cities.objects.all()
    return render(request, './get_form.html', context={'today': today,
                                                                    'all_cities': all_cities})

def processing_page(request):
    import playwright
    from playwright.sync_api import Page, expect, sync_playwright
    from bs4 import BeautifulSoup
    from prettytable import PrettyTable
    import requests
    import json
    from time import sleep
    from datetime import datetime
    from core.models import Cities, TrainTrips, PointsOfInterest, RoutesDict



    ## Блок №1: получение данных о пути туда
    # 1. задание вводных данных
    x = request.POST['dep-city']
    date_start = datetime.strptime(request.POST['dep-day'], '%Y-%m-%d').strftime("%B %d, %Y").replace(' 0', ' ')
    date_back = datetime.strptime(request.POST['arr-day'], '%Y-%m-%d').strftime("%B %d, %Y").replace(' 0', ' ')
    now_m = int(datetime.now().strftime("%m"))
    city = Cities.objects.get(city=x)
    y=[]
    for i in RoutesDict.objects.filter(city_id_from=city.id):
        c = Cities.objects.get(id=i.city_id_to)
        y.append(c.city)
        print(y)
    #y = ['Utrecht', 'Berlin']
    key_tr = '504C4C443DF8452183B91AE58961F70D'
    #print(date_start)
    #print(date_back)
    #print(now_m)
    p = sync_playwright().start()
    browser = p.firefox.launch() #headless=False)
    page = browser.new_page()
    page.set_default_timeout(30000)

    # 2. запуск браузера и получение информации по жд билетам из текущего места нахождения пользователя
    lst_trains_start = []
    for i in range(len(y)):

        # 2.1. ввод городов маршрута
        page.goto("https://saveatrain.com") #, timeout=0)
        search_from = page.locator('input[placeholder="From"]')
        search_from.click()
        search_from.clear()
        search_from.type(x)
        search_to = page.locator('input[placeholder="To"]')
        search_to.click()
        search_to.clear()
        search_to.type(y[i])
        page.get_by_role("button", name="Search").click()

        # 2.2. ввод даты отправления
        page.wait_for_load_state('load')
        date = page.locator('input[id="main-form-departure-date"]')
        date.click()
        # переключаемся на следующий месяц в случае необходимости
        date_start_m = int(datetime.strptime(request.POST['dep-day'], '%Y-%m-%d').strftime("%m"))
        while date_start_m > now_m:
            date_start_m -= 1
            next_mon = page.locator('button[aria-label="Next month"]')
            sleep(3)
            next_mon.click()

        txt_date2 = 'td[aria-label="' + date_start + '"]'
        date2 = page.locator(txt_date2)
        sleep(3)
        date2.click()

        page.get_by_role("button", name="Find my tickets").click()

        # 4.
        page.is_visible('div.results-container')

        col_names = ['departure_city', 'destination_city', 'price', 'departure_day', 'departure_time', 'arrival_day',
                         'arrival_time']
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
            try:
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
                dics_details['departure_day'] = dep_d
                lst_row.append(dep_t)
                dics_details['departure_time'] = dep_t
                lst_row.append(arr_d)
                dics_details['arrival_day'] = arr_d
                lst_row.append(arr_t)
                dics_details['arrival_time'] = arr_t
                table.add_row(lst_row)
                lst_trains_start.append(dics_details)
            except:
                break
    print(lst_trains_start)
    #######################################################################################################################
    ## Блок №2: получение данных о пути обратно

    # 2. запуск браузера и получение информации по жд билетам из места путешествия в изначальную точку
    lst_trains_back = []
    for i in range(len(y)):

        # 2.1. ввод городов маршрута
        page.goto("https://saveatrain.com") #, timeout=0)
        search_from = page.locator('input[placeholder="From"]')
        search_from.click()
        search_from.clear()
        search_from.type(y[i])
        search_to = page.locator('input[placeholder="To"]')
        search_to.click()
        search_to.clear()
        search_to.type(x)
        page.get_by_role("button", name="Search").click()

        # 2.2. ввод даты отправления
        page.wait_for_load_state('load')
        date = page.locator('input[id="main-form-departure-date"]')
        date.click()
        # переключаемся на следующий месяц в случае необходимости
        date_back_m = int(datetime.strptime(request.POST['arr-day'], '%Y-%m-%d').strftime("%m"))
        while date_back_m > now_m:
            date_back_m -= 1
            next_mon = page.locator('button[aria-label="Next month"]')
            sleep(3)
            next_mon.click()
        txt_date2 = 'td[aria-label="' + date_back + '"]'
        print(txt_date2)
        date2 = page.locator(txt_date2)
        sleep(3)
        date2.click()

        page.get_by_role("button", name="Find my tickets").click()

        # 4.
        page.is_visible('div.results-container')

        col_names = ['departure_city', 'destination_city', 'price', 'departure_day', 'departure_time', 'arrival_day',
                     'arrival_time']
        departure_city = y[i]
        destination_city = x
        print(destination_city)
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
            try:
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
                dics_details['departure_day'] = dep_d
                lst_row.append(dep_t)
                dics_details['departure_time'] = dep_t
                lst_row.append(arr_d)
                dics_details['arrival_day'] = arr_d
                lst_row.append(arr_t)
                dics_details['arrival_time'] = arr_t
                table.add_row(lst_row)
                lst_trains_back.append(dics_details)
            except:
                break
    print(lst_trains_back)
    page.close()
    browser.close()
    p.stop()

    #######################################################################################################################
    ## Блок №3: получение данных о точках интереса внутри городов
    # 1. задаём город, который будет приходить из предыдущего этапа и ключ партнёра tripadvisor
    lst_objects = []
    for i in range(len(y)):
        city = y[i]

        # 2. задаём url и получаем результат вызова 10 точек интереса для заданного города (трипадвизор выдаёт максимум 10 шт)
        url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key_tr}&searchQuery={city}&category=attractions&address={city}&language=en"
        headers = {"accept": "application/json"}
        response_trip = requests.get(url, headers=headers)

        # 3. создаём из строки со всеми данными лист с id точек интереса, по которому будем итерироваться при поиске деталей
        lst = []
        for j in range(6):
            lst.append(json.loads(response_trip.text)['data'][j]['location_id'])

        # 4. создаём справочные списки: с интересующими параметрами и с ключами итогового словаря
        parameters = ["['address_obj']['city']", "['name']", "['address_obj']['street1']", "['ranking_data']['ranking_string']"
            , "['rating']", "['groups'][0]['categories'][0]['name']"]
        col_names = ['city', 'name', 'address', 'ranking', 'rating', 'subcategory']

        # 5. вызываем location details реквест для получения нужных параметров и готовим данные для отрисовки в терминале
        for j in range(len(lst)):  # это объекты
            url = f"https://api.content.tripadvisor.com/api/v1/location/{lst[j]}/details?key={key_tr}&language=en&currency=USD"
            headers = {"accept": "application/json"}
            response_trip = requests.get(url, headers=headers)
            dics_details = {}
            lst_row = []
            for k in range(len(parameters)):
                info = f'json.loads(response_trip.text){parameters[k]}'
                key = col_names[k]
                try:
                    dics_details[key] = eval(info)
                    lst_row.append(eval(info))
                except Exception:
                    dics_details[key] = ''
                    lst_row.append('')
            lst_objects.append(dics_details)
    print(lst_objects)

    return render(request, './processing_page.html', {'departure_city':x,
                                                                        'date_start': date_start,
                                                                        'date_back': date_back,
                                                                        'destination_cities':y,
                                                                        'lst_trains_start':lst_trains_start,
                                                                        'lst_trains_back':lst_trains_back,
                                                                        'lst_objects':lst_objects})