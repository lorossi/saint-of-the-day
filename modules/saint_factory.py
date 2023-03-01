import logging
import os
import random
from datetime import datetime

import openai
import requests
import toml
from PIL import Image, ImageDraw, ImageFont

from .saint import Gender, Saint


class SaintFactory:
    def __init__(self):
        self._settings = self._loadSettings("settings.toml")
        self._createFolderStructure()

    def _loadFile(self, path: str) -> list[str]:
        """Loads a list of names from a file."""
        with open(path) as f:
            return [line.strip() for line in f]

    def _loadSettings(self, path: str) -> dict[str, str]:
        with open(path) as f:
            return toml.load(f)["SaintFactory"]

    def _createFolderStructure(self):
        logging.info("Creating folder structure")
        os.makedirs(self._settings["openai_folder"], exist_ok=True)
        os.makedirs(self._settings["image_folder"], exist_ok=True)
        os.makedirs(self._settings["toml_folder"], exist_ok=True)

    def _downloadImage(self, url: str, path: str) -> None:
        logging.info(f"Downloading image from {url}")
        r = requests.get(url, allow_redirects=True)
        open(path, "wb").write(r.content)
        logging.info(f"Image downloaded to {path}")

    def _generatePrompt(self, saint: Saint) -> str:
        logging.info("Generating prompt")

        if saint.gender == Gender.Male:
            gender = "man"
        else:
            gender = "woman"

        base_prompt = (
            f"Picture of {saint.full_name} (a {gender} and a saint), "
            f"protector of {', '.join(saint.protector_of_english)} "
        )
        styles = [
            "in the style of an Italian Renaissance painting",
            "in the style of a Baroque painting",
            "in the style of a Dutch Golden Age painting",
            "in the style of a russian icon",
            "in a photo-realistic style",
        ]
        prompt = f"{base_prompt} {random.choice(styles)}."
        logging.info(f"Prompt generated: {prompt}")
        return prompt

    def _downloadAIImage(self, saint: Saint) -> str:
        logging.info("Downloading AI image")
        openai.api_key = self._settings["openai_key"]
        logging.info("Requesting image from OpenAI")
        image_resp = openai.Image.create(
            prompt=self._generatePrompt(saint),
            n=1,
            size="512x512",
        )
        logging.info("Image received from OpenAI")
        url = image_resp["data"][0]["url"]
        filename = self._AIimageFilename()
        self._downloadImage(url, filename)
        return filename

    def _fitFont(
        self, text: str, font_size: int, font_path: str, max_width: float
    ) -> int:
        font_size = 100
        while True:
            font = ImageFont.FreeTypeFont(font_path, font_size)
            _, __, w, ___ = font.getbbox(
                text=text,
            )

            if w < max_width:
                break

            font_size -= 1

        return font_size

    def _generateImage(self, saint: Saint) -> str:
        logging.info("Generating image")

        if not os.path.isfile(self._AIimageFilename()):
            self._downloadAIImage(saint)

        base_img = Image.open(self._AIimageFilename())
        border_x = 32
        border_y = 192

        out_size = (base_img.width + border_x * 2, base_img.height + border_y)
        out_img = Image.new("RGBA", out_size, color=(249, 251, 255, 255))
        out_img.paste(base_img, (border_x, border_x))

        draw = ImageDraw.Draw(out_img)
        text = f"{saint.full_name} ({saint.born}-{saint.died})"
        subtext = saint.full_patron_city

        font_path = "resources/fonts/AcciaPiano-LightItalic.ttf"
        font_line_scl = 0.8
        font_size = self._fitFont(
            text=text,
            font_size=100,
            font_path=font_path,
            max_width=(out_img.width - border_x * 2) * font_line_scl,
        )

        font = ImageFont.FreeTypeFont(font_path, font_size)
        _, __, w, h = font.getbbox(
            text=text,
        )

        text_x = out_img.width / 2 - w / 2
        text_y = (
            out_img.height
            - (out_img.height - base_img.height - border_x) * 0.66
            - h / 2
        )

        draw.text(
            xy=(text_x, text_y),
            text=text,
            font=font,
            fill=(0, 0, 0, 255),
        )

        font_line_scl = 0.4
        font_size = self._fitFont(
            text=subtext,
            font_size=100,
            font_path=font_path,
            max_width=(out_img.width - border_x * 2) * font_line_scl,
        )

        font = ImageFont.FreeTypeFont(font_path, font_size)
        _, __, w, h = font.getbbox(
            text=subtext,
        )

        text_x = out_img.width / 2 - w / 2
        text_y = (
            out_img.height
            - (out_img.height - base_img.height - border_x) * 0.33
            - h / 2
        )

        draw.text(
            xy=(text_x, text_y),
            text=subtext,
            font=font,
            fill=(0, 0, 0, 255),
        )

        filename = self._outImageFilename()
        out_img.save(filename)
        logging.info(f"Image saved to {filename}")

    def generateSaint(self) -> Saint:
        logging.info("Generating saint")
        if os.path.isfile(self._outSaintFilename()):
            logging.info("Loading saint from file")
            return Saint.fromTOML(self._outSaintFilename())

        seed = datetime.now().strftime("%Y%m%d")
        random.seed(seed)

        gender = random.choice(["m", "f"])
        names = {
            "m": self._loadFile("resources/nomi-m.txt"),
            "f": self._loadFile("resources/nomi-f.txt"),
        }
        animals = self._loadFile("resources/animali-plurali.txt")
        animals_english = self._loadFile("resources/animali-plurali-inglese.txt")
        professions = self._loadFile("resources/professioni-plurali.txt")
        professions_english = self._loadFile(
            "resources/professioni-plurali-inglese.txt"
        )
        cities = self._loadFile("resources/citta.txt")

        name = random.choice(names[gender])

        protector_of_indexes = [
            random.randint(0, len(animals) - 1),
            random.randint(0, len(professions) - 1),
        ]

        protector_of = [
            animals[protector_of_indexes[0]],
            professions[protector_of_indexes[1]],
        ]
        protector_of_english = [
            animals_english[protector_of_indexes[0]],
            professions_english[protector_of_indexes[1]],
        ]

        patron_city = random.choice(cities)
        born = random.randint(100, 1800)
        died = born + random.randint(20, 100)
        birthplace = random.choice(cities)
        deathplace = random.choice(cities)

        logging.info("Generating saint")
        saint = Saint(
            gender=Gender(gender),
            name=name,
            protector_of=protector_of,
            patron_city=patron_city,
            born=born,
            died=died,
            birthplace=birthplace,
            deathplace=deathplace,
            protector_of_english=protector_of_english,
        )

        logging.info("Generating image")
        self._generateImage(saint)
        saint.image_path = self._outImageFilename()
        logging.info("Saving saint to file")
        saint.toTOML(self._outSaintFilename())
        logging.info("Saint generated")
        return saint

    def _AIimageFilename(self) -> str:
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["openai_folder"]
        return f"{folder}{timestamp}.png"

    def _outImageFilename(self) -> str:
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["image_folder"]
        return f"{folder}{timestamp}.png"

    def _outSaintFilename(self) -> str:
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["toml_folder"]
        return f"{folder}{timestamp}.toml"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")
    f = SaintFactory()
    saint = f.generateSaint()
    print(saint)
    logging.info("Done")
