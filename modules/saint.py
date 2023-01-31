from __future__ import annotations
from enum import Enum
from typing_extensions import Any
import toml


class Gender(Enum):
    Male = "m"
    Female = "f"


class Saint:
    def __init__(
        self,
        name: str,
        gender: Gender,
        protector_of: list[str],
        patron_city: str,
        born: int,
        died: int,
        birthplace: str,
        deathplace: str,
        image_path: str = None,
        protector_of_english: list[str] = None,
    ):
        self._name = name
        self._gender = Gender(gender)
        self._protector_of = [p.lower() for p in protector_of]
        self._patron_city = patron_city
        self._born = born
        self._died = died
        self._birthplace = birthplace
        self._deathplace = deathplace

        if image_path is not None:
            self._image_path = image_path

        if protector_of_english is not None:
            self._protector_of_english = protector_of_english

    def __repr__(self) -> str:
        bio = ""

        if self._male:
            bio += f"San {self._name}, protettore di "
        else:
            bio += f"Santa {self._name}, protettrice di "

        bio += ", ".join(self._protector_of[:-1])
        if len(self._protector_of) > 1:
            bio += " e "
        bio += self._protector_of[-1]

        if self._male:
            bio += ". Patrono di "
        else:
            bio += ". Patrona di "
        bio += self._patron_city

        if self._male:
            bio += ". Nato a "
        else:
            bio += ". Nata a "

        bio += f"{self._birthplace} ({self._born})"

        if self._male:
            bio += ", morto a "
        else:
            bio += ", morta a "
        bio += f"{self._deathplace} ({self._died})."

        return bio

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def bio(self) -> str:
        return self.__repr__()

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, path: str) -> None:
        self._image_path = path

    def __getattr__(self, name: str) -> Any:
        if name == "_male":
            return self._gender == Gender.Male
        if name == "full_name":
            if self._male:
                return f"San {self._name}"
            return f"Santa {self._name}"
        if name == "full_patron_city":
            if self._male:
                return f"Patrono di {self._patron_city}"
            return f"Patrona di {self._patron_city}"

        if (name := f"_{name}") in self.__dict__:
            return self.__dict__[name]

    def toTOML(self, path: str) -> None:
        data = {
            "name": self._name,
            "gender": self._gender.value,
            "protector_of": self._protector_of,
            "patron_city": self._patron_city,
            "born": self._born,
            "died": self._died,
            "birthplace": self._birthplace,
            "deathplace": self._deathplace,
            "image_path": self._image_path,
        }

        with open(path, "w") as f:
            toml.dump(data, f)

    @classmethod
    def fromTOML(cls, path: str) -> Saint:
        with open(path, "r") as f:
            data = toml.load(f)

        return cls(**data)
