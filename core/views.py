import json
from datetime import datetime
from time import sleep
import os

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from playwright.sync_api import sync_playwright

cities = dict(Amsterdam=['Rotterdam', 'Dortmund'], Antwerp=['Brussels', 'Rotterdam'], Berlin=['Leipzig', 'Dresden'],
              Bremen=['Hanover', 'Hamburg'], Brussels=['Antwerp', 'Rotterdam'], Cologne=['Dusseldorf', 'Frankfurt'],
              Dortmund=['Dusseldorf', 'Hanover'], Dresden=['Leipzig', 'Berlin'], Dusseldorf=['Cologne', 'Dortmund'],
              Essen=['Dortmund', 'Dusseldorf'], Frankfurt=['Cologne', 'Leipzig'], Hamburg=['Bremen', 'Berlin'],
              Hanover=['Bremen', 'Hamburg'], Leipzig=['Berlin', 'Hanover'], Munich=['Nuremberg', 'Stuttgart'],
              Nuremberg=['Stuttgart', 'Munich'], Paris=['Brussels', 'Stuttgart'], Rotterdam=['Antwerp', 'Amsterdam'],
              Stuttgart=['Frankfurt', 'Munich'])


def index(request):
    if request.method == "GET":
        return first_page(request)
    else:
        return processing_page(request)


def first_page(request):
    today = datetime.today().strftime('%Y-%m-%d')
    return render(request, './get_form.html', context={'today': today, 'cities': cities})


def find_train_tickets(dep_city, forward, date_train):
    dest_cities = cities[dep_city]
    url = "https://saveatrain.com"
    now_m = int(datetime.now().strftime("%m"))

    p = sync_playwright().start()
    browser = p.firefox.launch()
    page = browser.new_page()

    lst_trains = []
    for i in dest_cities:
        # 1. entering route cities
        page.goto(url)
        search_from = page.locator('input[placeholder="From"]')
        search_from.click()
        search_from.clear()
        if forward:
            search_from.type(dep_city)
        else:
            search_from.type(i)
        search_to = page.locator('input[placeholder="To"]')
        search_to.click()
        search_to.clear()
        if forward:
            search_to.type(i)
        else:
            search_to.type(dep_city)
        page.get_by_role("button", name="Search").click()

        # 2. entering the date and switching to the next month (if necessary)
        page.wait_for_load_state('load')
        date = page.locator('input[id="main-form-departure-date"]')
        date.click()
        date_start_m = int(datetime.strptime(date_train, "%B %d, %Y").strftime("%m"))

        while date_start_m > now_m:
            date_start_m -= 1
            next_mon = page.locator('button[aria-label="Next month"]')
            sleep(3)
            next_mon.click()

        txt_date2 = 'td[aria-label="' + date_train + '"]'
        date2 = page.locator(txt_date2)
        sleep(3)
        date2.click()
        page.get_by_role("button", name="Find my tickets").click()

        # 3. geting details about routes
        page.is_visible('div.results-container')

        if forward:
            destination_city = i
            departure_city = dep_city
        else:
            destination_city = dep_city
            departure_city = i
        parameters = ['price', 'departure-d', 'departure-t', 'arrival-d', 'arrival-t']

        for j in range(1, 4):
            dics_details = {}
            dics_details['departure_city'] = departure_city
            dics_details['destination_city'] = destination_city
            try:
                html_ind = '#result-' + str(j)
                html = page.inner_html(html_ind)
                soup = BeautifulSoup(html, 'html.parser')
                for k in parameters:
                    location = k + '-' + str(j)
                    value = soup.find('p', {'id': location}).text
                    key = k.replace('-', '_')
                    dics_details[key] = value
                lst_trains.append(dics_details)
            except:
                break
    page.close()
    browser.close()
    p.stop()
    return lst_trains


def find_points_of_interest(city, lst_objects):
    key_tr = os.environ['key_tr']
    # 1. getting attraction identifiers
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key_tr}&searchQuery={city}&category=attractions&address={city}&language=en"
    headers = {"accept": "application/json"}
    response_trip = requests.get(url, headers=headers)
    attractions_list = []
    for j in range(6):
        attractions_list.append(json.loads(response_trip.text)['data'][j]['location_id'])

    # 2. geting details about attractions
    parameters = ["['address_obj']['city']", "['name']", "['address_obj']['street1']", "['rating']",
                  "['groups'][0]['categories'][0]['name']"]
    col_names = ['city', 'name', 'address', 'rating', 'subcategory']

    for j in range(len(attractions_list)):  # это объекты
        url = f"https://api.content.tripadvisor.com/api/v1/location/{attractions_list[j]}/details?key={key_tr}&language=en&currency=USD"
        headers = {"accept": "application/json"}
        response_trip = requests.get(url, headers=headers)
        all_details = json.loads(response_trip.text)
        dics_details = {}
        for k in range(len(parameters)):
            key = col_names[k]
            try:
                dics_details[key] = eval(f'all_details{parameters[k]}')
            except:
                dics_details[key] = ''
        lst_objects.append(dics_details)
    return lst_objects


def processing_page(request):
    dep_city = request.POST['dep-city']
    date_start = datetime.strptime(request.POST['dep-day'], '%Y-%m-%d').strftime("%B %d, %Y").replace(' 0', ' ')
    date_back = datetime.strptime(request.POST['arr-day'], '%Y-%m-%d').strftime("%B %d, %Y").replace(' 0', ' ')
    dest_cities = cities[dep_city]

    lst_trains_start = find_train_tickets(dep_city, 1, date_start)
    lst_trains_back = find_train_tickets(dep_city, 0, date_back)

    lst_objects = []
    for city in dest_cities:
        lst_objects.append(find_points_of_interest(city, lst_objects))

    return render(request, './processing_page.html', {'departure_city': dep_city,
                                                      'date_start': date_start,
                                                      'date_back': date_back,
                                                      'destination_cities': dest_cities,
                                                      'lst_trains_start': lst_trains_start,
                                                      'lst_trains_back': lst_trains_back,
                                                      'lst_objects': lst_objects})
