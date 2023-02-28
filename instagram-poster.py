import schedule
import time

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory


def publish():
    s = SaintFactory()
    saint = s.generateSaint()
    caption = saint.bio + "\n\n#santodelgiorno"
    i = Instagram()
    i.uploadImage(image_path=saint.image_path, image_caption=caption)


def main():
    schedule.every().day.at("08.00").do(publish)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
