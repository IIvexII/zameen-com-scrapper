import requests
from bs4 import BeautifulSoup


def convert_price(price):
    """
    Convert crore, lakhs, millions and Thousand into numbers

    :param price: str
    :return: float
    """
    if price.endswith('Crore'):
        return round(float(price[:-5]) * 10000000)
    elif price.endswith('Lakh'):
        return round(float(price[:-4]) * 100000)
    elif price.endswith('Million'):
        return round(float(price[:-7]) * 1000000)
    elif price.endswith('Arab'):
        return round(float(price[:-4]) * 1000000000)
    elif price.endswith('Thousand'):
        return round(float(price[:-8]) * 1000)
    else:
        return round(float(price))

# convert kanal, merla, Sq. Yd., S  into square feets


def convert_size(size):
    """
    Convert kanal merla into sqft

    :param size: str
    :return: float
    """
    if size.endswith('Marla'):
        return round(float(size[:-5].replace(",", "")) * 225)
    elif size.endswith('Kanal'):
        return round(float(size[:-5].replace(",", "")) * 4500)
    elif size.endswith('Sq. Yd.'):
        return round(float(size[:-7].replace(",", "")) * 9)
    else:
        return round(float(size))


def text(tag, datatype="str"):
    """
    This function will return the text of the tag.

    :param tag: tag object
    :param datatype: num or str or price, size
    :return: price in number or string
    """
    if tag is None and datatype == "num":
        return 0
    if datatype == "num":
        try:
            return int(tag.text.strip())
        except ValueError:
            return 0
    if tag is None and datatype == "str":
        return ""
    if datatype == "str":
        return tag.text.strip()
    if tag is None and datatype == "price":
        return 0.0
    if datatype == "price":
        return convert_price(tag.text.strip())
    if tag is None and datatype == "size":
        return 0.0
    if datatype == "size":
        return convert_size(tag.text.strip())


def scrap(city, pages_range):
    """
    This function will scrap the zameen.com website and
    return the list of houses information

    :param city: str
    :param pages_range: int
    :return: list
    """
    house_info = []

    for page_number in range(1, pages_range+1):
        url = f'https://www.zameen.com/Homes/{city}-{page_number}.html'
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        house_list = soup.select("main > div > div > div > div > ul > li")

        # store lenght of previous length of house info list
        prev_len = len(house_info)

        for house in house_list:
            baths = house.select_one("span[aria-label='Baths']")
            beds = house.select_one("span[aria-label='Beds']")
            location = house.select_one("div[aria-label='Location']")
            price = house.select_one("span[aria-label='Price']")
            size = house.select_one("div[title]>div > div > span:nth-child(1)")

            if price:
                if size is None:
                    size = location.parent.select_one(
                        "div:nth-child(2) > div > span:nth-child(3)")
                house_info.append(
                    {
                        "location": text(location),
                        "price":    text(price, datatype="price"),
                        "bedrooms":     text(beds, datatype="num"),
                        "baths":    text(baths, datatype="num"),
                        "size":     text(size, datatype="size")
                    }
                )

        # get out of the loop if the last accessed page
        # doesnot exist to avoid useless requests because
        # next pages will not exist as well
        if len(house_info) == prev_len:
            break

    return house_info


if __name__ == "__main__":
    house_info = []

    cities = [
        {'id': 1, 'name': 'Lahore'},
        {'id': 2, 'name': 'Karachi'},
        {'id': 3, 'name': 'Islamabad'},
        {'id': 15, 'name': 'Multan'},
        {'id': 16, 'name': 'Faisalabad'},
        {'id': 17, 'name': 'Peshawar'},
        {'id': 18, 'name': 'Quetta'},
        {'id': 41, 'name': 'Rawalpindi'},
        {'id': 36, 'name': 'Murree'},
        {'id': 327, 'name': 'Gujranwala'},
        {'id': 1233, 'name': 'Attock'},
        {'id': 3234, 'name': '2_FECHS'},

    ]

    for city in cities:

        # change 20 to any number of pages you want to scrap
        house_info.append(
            {
                "city": city.get('name'),
                "info": scrap(f"{city.get('name')}-{city.get('id')}", 100)
            }
        )

    with open("zameen.csv", "w") as f:
        # write csv header
        f.write("city|location|price|bedrooms|baths|size\n")
        for house in house_info:
            for info in house.get('info'):
                f.write(
                    f"{house.get('city')}|{info.get('location')}|{info.get('price')}|{info.get('bedrooms')}|{info.get('baths')}|{info.get('size')}\n")
