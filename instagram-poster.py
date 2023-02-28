import schedule
import time
import logging

from modules.instagram import Instagram
from modules.saint_factory import SaintFactory


def publish():
    logging.info("Publishing post")
    s = SaintFactory()
    saint = s.generateSaint()
    caption = saint.bio + "\n\n#santodelgiorno #santino_quotidiano"
    i = Instagram()
    i.uploadImage(image_path=saint.image_path, image_caption=caption)
    logging.info("Post published")


def main():
    logging.info("Starting instagram poster")
    schedule.every().day.at("08:00").do(publish)
    logging.info("Posts scheduled")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    filename = __file__.replace(".py", ".log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=filename,
        filemode="w",
    )

    main()
