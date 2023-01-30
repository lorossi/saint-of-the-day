from bs4 import BeautifulSoup
import requests


def td_to_names(elements: list[BeautifulSoup]) -> list[str]:
    names = []
    for e in elements:
        temp = e.text.split(",")

        for t in temp:
            if t.strip():
                names.append(t.strip())

    return names


def extract_names(url: str) -> tuple[list[str], list[str]]:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for sup in soup.find_all("sup"):
        sup.decompose()

    for index in soup.find_all("table", {"class": "itwiki_template_toc"}):
        index.decompose()

    for bottom in soup.find_all("table", {"class": "noprint"}):
        bottom.decompose()

    males = []
    females = []

    for row in soup.find_all("tr"):
        td = row.find_all("td")
        males.extend(td_to_names(td[:2]))
        females.extend(td_to_names(td[2:]))

    return males, females


def main():
    names = {
        "m": [],
        "f": [],
    }
    urls = [
        "https://it.wikipedia.org/wiki/Prenomi_italiani_(A-L)",
        "https://it.wikipedia.org/wiki/Prenomi_italiani_(M-Z)",
    ]

    for u in urls:
        male, female = extract_names(u)
        names["m"].extend(male)
        names["f"].extend(female)

    for gender in names:
        names[gender].sort()
        with open(f"nomi-{gender}.txt", "w") as f:
            f.write("\n".join(names[gender]))


if __name__ == "__main__":
    main()
