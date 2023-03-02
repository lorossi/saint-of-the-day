from bs4 import BeautifulSoup
import requests


def extract_cities(url: str) -> list[str]:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    cities = []

    for thead in soup.find_all("thead"):
        thead.decompose()

    while table := soup.find("table", {"class": "wikitable"}):
        for tr in table.find_all("tr"):
            td = tr.find("td")
            if not td:
                continue

            cities.append(td.text.strip())
        table.decompose()

    return cities


def main() -> None:
    urls = [
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_A-B",
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_C-D-E-F"
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_G-H-I-J-K",
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_L-M-N-O",
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_P-Q-R-S",
        "https://en.wikipedia.org/wiki/List_of_towns_and_cities_with_"
        "100,000_or_more_inhabitants/country:_T-U-V-W-X-Y-Z",
    ]

    cities = []
    for url in urls:
        cities.extend(extract_cities(url))

    cities.sort()

    with open("citta.txt", "w") as f:
        f.write("\n".join(cities))


if __name__ == "__main__":
    main()
