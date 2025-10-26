import requests
from bs4 import BeautifulSoup

from the_concert import get_page_destination_data, save_concert

if __name__ == "__main__":
    with open("index.html", "r", encoding="utf-8") as file:

        content = file.read()
        soup = BeautifulSoup(content, "html.parser")

        a_elements = soup.find_all("a")

        for a in a_elements:
            href = a.get("href")

            # -- one at the time --
            url = f"https://www.theconcert.com{href}"

            res = requests.get(url)

            if res.status_code == 200:
                data = get_page_destination_data(url, headless=True, timeout=10)
                if data:
                    save_concert(data)
             
            else:
                print(f"Failed to retrieve the page. Status code: {res.status_code}")
