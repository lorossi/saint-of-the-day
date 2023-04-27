"""Module containing the SaintFactory class."""
from __future__ import annotations

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
    """Class handling the logic to generate images of saints."""

    def __init__(self) -> SaintFactory:
        """Initialize the saint factory.

        Returns:
            SaintFactory
        """
        self._settings = self._loadSettings("settings.toml")
        self._createFolderStructure()

    def _loadFile(self, path: str) -> list[str]:
        """Load a file.

        Args:
            path (str): Path to the file.

        Returns:
            list[str]: Lines of the file.
        """
        with open(path) as f:
            return [line.strip() for line in f]

    def _loadSettings(self, path: str) -> dict[str, str]:
        """Load settings from a TOML file.

        Args:
            path (str): Path to the TOML file.

        Returns:
            dict[str, str]: Settings.
        """
        with open(path) as f:
            return toml.load(f)["SaintFactory"]

    def _createFolderStructure(self) -> None:
        """Create folder structure. \
        The needed folders are in the settings.toml file."""
        logging.info("Creating folder structure")
        os.makedirs(self._settings["openai_folder"], exist_ok=True)
        os.makedirs(self._settings["image_folder"], exist_ok=True)
        os.makedirs(self._settings["toml_folder"], exist_ok=True)

    def _downloadImage(self, url: str, path: str) -> None:
        """Download an image from a URL.

        Args:
            url (str): url of the image
            path (str): destination path
        """
        logging.info(f"Downloading image from {url}")
        r = requests.get(url, allow_redirects=True)
        open(path, "wb").write(r.content)
        logging.info(f"Image downloaded to {path}")

    def _generatePrompt(self, saint: Saint) -> str:
        """Generate the prompt for the AI.

        Args:
            saint (Saint): Saint to generate the image for.

        Returns:
            str
        """
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
            "in the style of a Japanese woodblock print",
            "in the style of a Chinese ink painting",
            "in the style of a Persian miniature",
            "in the style of a Byzantine mosaic",
            "in the style of a medieval manuscript",
            "in the style of a stained glass window",
            "in the style of a Banksy painting",
            "in the style of a Picasso painting",
            "in the style of a Salvador Dali painting",
            "in the style of a 8-bit pixel art",
            "in the style of a 16-bit pixel art",
            "in the style of an Andy Warhol painting",
            "in the style of a Roy Lichtenstein painting",
            "in the style of a Jackson Pollock painting",
            "in the style of a Keith Haring painting",
            "in the style of a Piet Mondrian painting",
            "in the outrun style",
            "in the style of a Kandinsky painting",
            "in the style of a 2000s rap album cover",
            "in the style of a 2000s pop album cover",
            "in the style of a grunge album cover",
            "in a low-poly style",
            "in the style of a 90s anime",
            "in the style of a disney movie",
            "in the style of a Leonardo Da Vinci drawing",
            "in the style of a Van Gogh painting",
            "in the style of a Monet painting",
            "in the style of a Cezanne painting",
            "in the style of a Matisse painting",
            "in the style of a Klimt painting",
            "in the style of a 1920s black and white movie",
            "in the style of a 1950s black and white movie",
            "in the style of a 1970s sci-fi movie",
            "in the style of a Marvel comic book",
        ]
        prompt = f"{base_prompt} {random.choice(styles)}."
        logging.info(f"Prompt generated: {prompt}")
        return prompt

    def _downloadAIImage(self, saint: Saint) -> str:
        """Create and download the image from the AI.

        Args:
            saint (Saint): Saint to generate the image for.

        Returns:
            str: Path to the image.
        """
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
        self._downloadImage(url, self._AIimageFilename)
        return self._AIimageFilename

    def _fitFont(
        self, text: str, font_size: int, font_path: str, max_width: float
    ) -> int:
        """Fit a font to a given width.

        Args:
            text (str): text to fit
            font_size (int)
            font_path (str)
            max_width (float): maximum width of the text (in pixels)

        Returns:
            int: size of the font
        """
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
        """Generate the image of a saint.

        Args:
            saint (Saint): Saint to generate the image for.

        Returns:
            str: Path to the image.
        """
        logging.info("Generating image")

        # if source image doesn't exist, download it
        if not os.path.isfile(self._AIimageFilename):
            self._downloadAIImage(saint)

        # open source image
        base_img = Image.open(self._AIimageFilename)
        border_x = 32
        border_y = 192

        # create output image
        out_size = (base_img.width + border_x * 2, base_img.height + border_y)
        out_img = Image.new("RGBA", out_size, color=(249, 251, 255, 255))
        out_img.paste(base_img, (border_x, border_x))

        # initiate the drawing process
        draw = ImageDraw.Draw(out_img)
        text = f"{saint.full_name} ({saint.born}-{saint.died})"
        subtext = saint.full_patron_city

        # fit the font to the image width
        font_path = "resources/fonts/AcciaPiano-LightItalic.ttf"
        font_line_scl = 0.8
        font_size = self._fitFont(
            text=text,
            font_size=100,
            font_path=font_path,
            max_width=(out_img.width - border_x * 2) * font_line_scl,
        )

        # draw the text, centred
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

        # draw the subtext, centred
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

        # save the image
        filename = self._outImageFilename
        out_img.save(filename)
        logging.info(f"Image saved to {filename}")

    def generateSaint(self) -> Saint:
        """Generate a saint.

        Returns:
            Saint
        """
        logging.info("Generating saint")
        # if the saint is already generated, load it from file
        if os.path.isfile(self._outSaintFilename):
            logging.info("Loading saint from file")
            return Saint.fromTOML(self._outSaintFilename)

        # random seeding to make the generation reproducible
        seed = datetime.now().strftime("%Y%m%d")
        random.seed(seed)

        # choose the parameters of the saint
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
        # create the saint object
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
        # associate the image to the saint
        saint.image_path = self._outImageFilename

        logging.info("Saving saint to file")
        saint.toTOML(self._outSaintFilename)

        logging.info("Saint generated")
        return saint

    @property
    def _AIimageFilename(self) -> str:
        """Get the filename of the image generated by OpenAI.

        Returns:
            str
        """
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["openai_folder"]
        return f"{folder}{timestamp}.png"

    @property
    def _outImageFilename(self) -> str:
        """Get the filename of the image generated by the script.

        Returns:
            str
        """
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["image_folder"]
        return f"{folder}{timestamp}.png"

    @property
    def _outSaintFilename(self) -> str:
        """Get the filename of the saint generated by the script.

        Returns:
            str
        """
        timestamp = datetime.today().strftime("%Y%m%d")
        folder = self._settings["toml_folder"]
        return f"{folder}{timestamp}.toml"
