import re


def plural(name: str) -> str:
    rules = {
        r"io$": "i",
        r"logo$": "loghi",
        r"fago$": "fagi",
        r"co$": "chi",
        r"go$": "gi",
        r"ca$": "che",
        r"ga$": "ghe",
        r"e$": "i",
        r"o$": "i",
        r"a$": "e",
    }

    for pattern, replacement in rules.items():
        if re.search(pattern, name):
            return re.sub(pattern, replacement, name)

    return name


def main() -> None:
    with open("professioni.txt") as f:
        professions = f.read().splitlines()

    with open("professioni-plurali.txt", "w") as f:
        for p in professions:
            f.write(plural(p) + "\n")


if __name__ == "__main__":
    main()
