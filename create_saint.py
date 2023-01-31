from modules.saint_factory import SaintFactory


def main():
    f = SaintFactory()
    saint = f.generateSaint()
    print(saint)


if __name__ == "__main__":
    main()
