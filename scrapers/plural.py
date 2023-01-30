from bs4 import BeautifulSoup
import requests
import re


def remove_spaces(s: str) -> str:
    x = s.strip()
    if " " in x:
        return x.split(" ")[0]
    return x


def format_plural(plural: str) -> str:
    ...
    if matches := re.search(r"^(\s*,?\s*:?\s*)?([a-z]+)(\s*,\s*)?$", plural):
        return matches.group(2)
    return plural


def get_plural(soup: BeautifulSoup) -> str:
    inflections = soup.find("div", {"class": "inflectionsSection"})
    if not inflections:
        return

    pl = inflections.find("span", string=" pl")
    if pl:
        return format_plural(pl.next_sibling.text)

    mpl = inflections.find("span", string=" mpl")
    if mpl:
        return format_plural(mpl.next_sibling.text)

    fpl = inflections.find("span", string=" fpl")
    if fpl:
        return format_plural(fpl.next_sibling.text)


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


def extract_plural(singular: str) -> str:
    url = f"https://www.wordreference.com/definizione/{singular}"
    soup = get_soup(url)
    plural = get_plural(soup)

    if not plural:
        return singular.lower()

    return plural


def convert_file(file_in: str, file_out: str) -> None:
    with open(file_in) as f:
        words = f.read().splitlines()

    plural = []
    for w in words:
        print(f"{w} -> ", end="")
        try:
            p = extract_plural(w)
            print(p)
        except Exception as e:
            p = w
            print(f"ERROR: {e}")
        plural.append(p)

    with open(file_out, "w") as f:
        for p in plural:
            f.write(p + "\n")


def main():
    convert_file("animali.txt", "animali-plurali.txt")


if __name__ == "__main__":
    main()
