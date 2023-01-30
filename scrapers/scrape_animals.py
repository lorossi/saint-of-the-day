from bs4 import BeautifulSoup
import requests
import re


def extract_animals(url: str) -> list[str]:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    animals = []

    while ul := soup.find("div", {"class": "multicolumna"}):
        for li in ul.find_all("li"):
            if not li.text:
                continue
            animal = re.sub(r"\s* \(.*\)$", "", li.text).strip()
            if not animal:
                continue
            if " " in animal:
                animal = animal.split(" ")[0]

            animals.append(animal)

        ul.decompose()

    return animals


def main():
    url = "https://www.animalpedia.it/nomi-di-animali-dalla-a-alla-z-3397.html"
    animals = extract_animals(url)

    animals = sorted(set(animals))

    with open("animali.txt", "w") as f:
        for a in animals:
            f.write(a + "\n")


if __name__ == "__main__":
    main()
