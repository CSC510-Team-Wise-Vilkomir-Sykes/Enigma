import asyncio

import requests
from bs4 import BeautifulSoup
from src.database import create_table, insert_song, clear_data


def get_chart_links(main_url='https://www.billboard.com/charts/'):
    """Scrapes the main Billboard charts page to retrieve all chart links."""
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'o-chart-list-card' divs for each chart link
    chart_divs = soup.find_all('div', class_='o-chart-list-card')
    chart_links = []
    for chart_div in chart_divs:
        link_element = chart_div.find('a', href=True)
        if link_element:
            href = link_element['href']
            chart_name = href.strip('/').split('/')[
                -1]  # Extract the last part of URL
            chart_links.append(chart_name)

    print(f"Found {len(chart_links)} chart links.")
    return chart_links


def scrape_chart(chart_link):
    """Scrapes a single chart page and returns a list of song dictionaries."""
    url = f'https://www.billboard.com/charts/{chart_link}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
                      'Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Locate all song entries
    song_entries = soup.find_all('ul', class_='o-chart-results-list-row')

    # Extract details for each song
    songs = []
    for entry in song_entries:

        list_items = entry.find_all('li')

        # Initialize a dictionary for each song
        song_data = {'chart_name': chart_link}

        # Iterate through each li, skipping the third column (index 2)
        for idx, item in enumerate(list_items):
            if idx == 2:
                continue  # Skip the third column

            # Extract data based on the position
            if idx == 0:
                # Rank
                song_data['rank'] = item.find(
                    'span', class_='c-label').get_text(strip=True)
            elif idx == 1:
                continue
            elif idx == 3:
                # Title and Artist (skip image content, if present)
                title_element = item.find('h3', id='title-of-a-story')
                artist_element = item.find('span', class_='c-label')

                if title_element:
                    song_data['title'] = title_element.get_text(strip=True)
                if artist_element:
                    song_data['artist'] = artist_element.get_text(strip=True)
        if list_items:
            last_item = list_items[-1]
            weeks_on_chart = last_item.find('span', class_='c-label')
            if weeks_on_chart and weeks_on_chart.get_text(strip=True).isdigit():
                song_data['weeks_on_chart'] = int(
                    weeks_on_chart.get_text(strip=True))

        # Append the song data to the songs list
        songs.append(song_data)

    return songs


async def initial_scrape():
    """Performs an initial scrape to fill the database with all charts."""
    main_url = 'https://www.billboard.com/charts/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
                      'Safari/537.36'
    }
    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all 'o-chart-list-card' divs for each chart link
    chart_divs = soup.find_all('div', class_='o-chart-list-card')
    chart_links = []
    for chart_div in chart_divs:
        link_element = chart_div.find('a', href=True)
        if link_element:
            href = link_element['href']
            chart_name = href.strip('/').split('/')[
                -1]  # Extract the last part of URL
            chart_links.append(chart_name)

    # Clear existing data and create the table

    clear_data()
    create_table()  # Scrape each chart and insert songs into the database
    for chart_link in chart_links:
        print(f"Scraping chart: {chart_link}")
        songs = scrape_chart(chart_link)
        for song_data in songs:
            insert_song(song_data)
        await asyncio.sleep(1)  # Pause slightly between chart scrapes
    print("Initial scrape complete. Database is populated with all chart data.")


def update_charts():
    """Regular update function that scrapes all current charts without clearing
    the database."""
    # Get all chart links dynamically
    chart_links = get_chart_links()
    create_table()  # Ensure the table exists

    # Scrape each chart and update database
    for chart_link in chart_links:
        print(f"Updating chart: {chart_link}")
        songs = scrape_chart(chart_link)
        for song_data in songs:
            insert_song(song_data)
    print("Update complete.")
