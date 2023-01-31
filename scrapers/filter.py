def main():
    with open("resources/professioni-plurali.txt") as f:
        lines = f.read().splitlines()

    plural = sorted(set(lines))
    with open("resources/professioni-plurali.txt", "w") as f:
        f.write("\n".join(plural))


if __name__ == "__main__":
    main()
