"""Module containing the Saint class."""
from __future__ import annotations

from enum import Enum

import toml
from typing_extensions import Any


class Gender(Enum):
    """Enum containing the two possible genders of each saint."""

    Male = "m"
    Female = "f"


class Saint:
    """Class containing a saint."""

    _name: str
    _gender: Gender
    _protector_of: list[str]
    _patron_city: str
    _born: int
    _died: int
    _birthplace: str
    _deathplace: str
    _image_path: str = None
    _protector_of_english: list[str] = None

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
    ) -> Saint:
        """Initialize the saint.

        Args:
            name (str): Name of the saint.
            gender (Gender): Gender of the saint.
            protector_of (list[str]): List of things the saint is the patron of.
            patron_city (str): City (or town, hamlet) the saint is the patron of.
            born (int): Birth year of the saint.
            died (int): Death year of the saint.
            birthplace (str): Birthplace of the saint.
            deathplace (str): Deathplace of the saint.
            image_path (str, optional): Path of the saint image. Defaults to None.
            protector_of_english (list[str], optional): English translation \
                 of the things the saint protects. Defaults to None.

        Returns:
            Saint: _description_
        """
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
        """Return the string representation of the saint."""
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
        """Return the string representation of the saint."""
        return self.__repr__()

    @property
    def bio(self) -> str:
        """Return the string representation of the saint."""
        return self.__repr__()

    @property
    def image_path(self) -> str:
        """Path of the saint image."""
        return self._image_path

    @image_path.setter
    def image_path(self, path: str) -> None:
        """Set the path of the saint image."""
        self._image_path = path

    def __getattr__(self, name: str) -> Any:
        """Get the attribute of the saint.

        In addition to the attributes passed in the constructor,
        it is possible to get the following attributes:

        - full_name: Full name of the saint.
        - full_patron_city: Full name of the patron city.

        Args:
            name (str): Name of the attribute.

        Returns:
            Any: Value of the attribute.
        """
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
        """Save the saint to a TOML file.

        Args:
            path (str): Path of the TOML file.
        """
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
        """Load a saint from a TOML file.

        Args:
            path (str): Path of the TOML file.

        Returns:
            Saint: Saint loaded from the TOML file.
        """
        with open(path, "r") as f:
            data = toml.load(f)

        return cls(**data)
