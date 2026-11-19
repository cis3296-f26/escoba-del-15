# ui words loaded from assets/lang/{code}.ini
from configparser import ConfigParser
from pathlib import Path

LANG_DIR = Path(__file__).resolve().parent / "assets" / "lang"

class Language:
    def __init__(self, strings: dict[str, str]):
        self._strings = strings

    @classmethod
    def load(cls, code: str) -> "Language":
        path = LANG_DIR / f"{code}.ini"
        if not path.is_file():
            path = LANG_DIR / "en.ini"

        parser = ConfigParser()
        parser.read(path, encoding="utf-8")
        strings = dict(parser["ui"]) if parser.has_section("ui") else {}
        return cls(strings)

    def __call__(self, string_id: str, **kwargs) -> str:
        template = self._strings.get(string_id, string_id)
        if kwargs:
            return template.format(**kwargs)
        return template