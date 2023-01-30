from .saint import Saint, Gender
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont
import openai
import os
import requests


class SaintFactory:
    @staticmethod
    def _loadFile(path: str) -> list[str]:
        """Loads a list of names from a file."""
        with open(path) as f:
            return [line.strip() for line in f]

    @staticmethod
    def _downloadImage(url: str, path: str) -> None:
        """Downloads an image from a url and saves it to a path."""
        r = requests.get(url, allow_redirects=True)
        open(path, "wb").write(r.content)

    @staticmethod
    def _generatePrompt(saint: Saint) -> str:
        base_prompt = f"Image of {saint.full_name} ({saint.born}-{saint.died})"
        styles = [
            "in the style of an Italian Renaissance painting",
            "in the style of a Baroque painting",
            "in the style of a Dutch Golden Age painting",
            "in the style of a Flemish painting",
            "in the style of a russian icon",
        ]
        return f"{base_prompt} {random.choice(styles)}."

    @staticmethod
    def _downloadAIImage(saint: Saint) -> str:
        api_key = SaintFactory._loadFile("resources/openai-api-key")[0]
        openai.api_key = api_key
        image_resp = openai.Image.create(
            prompt=SaintFactory._generatePrompt(saint),
            n=1,
            size="512x512",
        )
        ...
        url = image_resp["data"][0]["url"]
        ...
        filename = SaintFactory._AIimageFilename()
        SaintFactory._downloadImage(url, filename)
        return filename

    def _AIimageFilename() -> str:
        timestamp = datetime.today().strftime("%Y%m%d")
        return f"img/openai-{timestamp}.png"

    def _outImageFilename() -> str:
        timestamp = datetime.today().strftime("%Y%m%d")
        return f"img/{timestamp}.png"

    @staticmethod
    def _fitFont(text: str, font_size: int, font_path: str, max_width: float) -> int:
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

    @staticmethod
    def _generateImage(saint: Saint) -> str:
        if not os.path.isfile(SaintFactory._AIimageFilename()):
            SaintFactory._downloadAIImage(saint)

        base_img = Image.open(SaintFactory._AIimageFilename())
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
        font_size = SaintFactory._fitFont(
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
        font_size = SaintFactory._fitFont(
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

        out_img.save("img/out.png")

    @staticmethod
    def generateSaint(seed: str = None) -> Saint:
        if not seed:
            seed = datetime.now().strftime("%Y%m%d")
        random.seed(seed)

        gender = random.choice(["m", "f"])
        names = {
            "m": SaintFactory._loadFile("resources/nomi-m.txt"),
            "f": SaintFactory._loadFile("resources/nomi-f.txt"),
        }
        animals = SaintFactory._loadFile("resources/animali-plurali.txt")
        professions = SaintFactory._loadFile("resources/professioni-plurali.txt")
        cities = SaintFactory._loadFile("resources/citta.txt")

        name = random.choice(names[gender])
        protector_of = random.sample([*animals, *professions], random.randint(1, 4))
        patron_city = random.choice(cities)
        born = random.randint(100, 1800)
        died = born + random.randint(20, 100)
        birthplace = random.choice(cities)
        deathplace = random.choice(cities)

        saint = Saint(
            gender=Gender(gender),
            name=name,
            protector_of=protector_of,
            patron_city=patron_city,
            born=born,
            died=died,
            birthplace=birthplace,
            deathplace=deathplace,
        )

        SaintFactory._generateImage(saint)
        saint.image_path = SaintFactory._AIimageFilename()
        return saint
