import requests
from bs4 import BeautifulSoup
from database import create_table, insert_song, clear_data

def scrape_charts():
    # URL of the Billboard main charts page
    main_url = 'https://www.billboard.com/charts/'
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all chart links
    chart_divs = soup.find_all('div', class_='o-chart-list-card')
    chart_links = []
    for chart_div in chart_divs:
        link_element = chart_div.find('a', href=True)
        if link_element:
            href = link_element['href']
            chart_name = href.strip('/').split('/')[-1]
            chart_links.append(chart_name)

