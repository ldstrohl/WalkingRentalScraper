import requests
from bs4 import BeautifulSoup
import re

def search_rentals_with_breweries(zipcode, max_price):
    # Zillow URL for rental search
    url = f'https://www.zillow.com/homes/for_rent/{zipcode}_rb/1_p/'
    
    # test commit for github initialization
    
    # Custom User-Agent header
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36','Accept-Language':'en-US,en;q=0.9',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Accept-Encoding':'gzip, deflate, br',
    'upgrade-insecure-requests':'1'}
    # Send request to Zillow website
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rental_listings = soup.find_all('div',{'class':'property-card-data'})
        if rental_listings:
            # Iterate over rental listings
            for listing in rental_listings:
                address = listing.address.string
                # rental_info = {
                #     'address': address.get_text(strip=True),
                #     'city': address.find_next('div').get_text(strip=True),
                #     'state': address.find_next('div').find_next('div').get_text(strip=True),
                #     'zipcode': address.find_next('div').find_next('div').find_next('div').get_text(strip=True),
                # }


                # Find latitude and longitude of the rental listing
                lat = listing['data-latitude']
                lon = listing['data-longitude']

                # Get rental price
                price_pattern = r'\$[\d,]+(?:\.\d+)?'
                price_string = re.findall(price_pattern, listing.span.string)
                price = int(price_string[0].replace('$', '').replace(',', ''))
                
                # Convert price to integer and check if it is within the maximum price
                if price and price <= max_price:
                    # Search for breweries within one mile of the rental using lat and lon
                    breweries = search_breweries(lat, lon)

                    # Print rental information if breweries are found
                    if breweries:
                        print_rental_info(rental_info, price, breweries)
        else:
            print('No rental results found.')
    else:
        print('Error occurred while accessing Zillow website.')

def search_breweries_within_duration(address, duration):
    # Set the address and duration in minutes
    origin = address
    max_duration = duration * 60  # Convert duration to seconds

    # Prepare the search query URL
    base_url = 'https://maps.googleapis.com/maps/api/directions/json'
    api_key = 'YOUR_API_KEY'  # Replace with your actual API key
    url = f'{base_url}?origin={origin}&destination=breweries&mode=walking'

    # Send a GET request to the URL
    response = requests.get(url)

    # Get the JSON response
    data = response.json()

    # Process the response
    breweries = []
    if data['status'] == 'OK':
        routes = data['routes']
        for route in routes:
            duration_sec = route['legs'][0]['duration']['value']
            if duration_sec <= max_duration:
                # Extract brewery information from the route
                brewery = route['legs'][0]['end_address']
                breweries.append(brewery)

    return breweries

def print_rental_info(rental_info, price, breweries):
    # Print rental information
    print('Rental Details:')
    print('Address:', rental_info['address'])
    print('City:', rental_info['city'])
    print('State:', rental_info['state'])
    print('Zipcode:', rental_info['zipcode'])
    print('Price:', price)

    print('\nBreweries within one mile:')
    for brewery in breweries:
        print('-', brewery)

    print('---\n')

# Example usage
zipcode = '98030'  # Replace with your desired zipcode
max_price = 2000  # Replace with your desired maximum price
search_rentals_with_breweries(zipcode, max_price)