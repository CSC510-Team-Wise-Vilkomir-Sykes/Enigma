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
			chart_name = href.strip('/').split('/')[-1]  # Extract the last part of URL
			chart_links.append(chart_name)

	print(f"Found {len(chart_links)} chart links.")
	return chart_links

