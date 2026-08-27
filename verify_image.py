"""Provjeri da Gramps Web BCS slika sadrži očekivane zakrpe."""

from __future__ import annotations

import gettext
import json
from pathlib import Path

import gramps.plugins.rel.rel_hr as relationship_module


def contains_cyrillic(value: str) -> bool:
    return any("\u0400" <= character <= "\u052f" for character in value)


relationship_path = Path(relationship_module.__file__)
relationship_source = relationship_path.read_text(encoding="utf-8")
registry_source = relationship_path.with_name("relplugins.gpr.py").read_text(
    encoding="utf-8"
)

assert "GRAMPSWEB_BCS_SINGLE_RELATIONSHIPS_V4" in relationship_source
assert "GRAMPSWEB_BCS_SERBIAN_RELATIONSHIP_LOCALES_V4" in registry_source

frontend_path = Path("/app/static/lang/sr.json")
frontend_raw = frontend_path.read_text(encoding="utf-8")
frontend = json.loads(frontend_raw)
marker = Path("/app/static/lang/.grampsweb-bcs-serbian-latin-v1")

assert marker.is_file()
assert "GRAMPSWEB_BCS_SERBIAN_LATIN_UI_V1" in marker.read_text(encoding="utf-8")
assert not contains_cyrillic(frontend_raw)

expected_frontend = {
    "Running tasks": "Aktivni zadaci",
    "Export media": "Izvezi medije",
    "Process transactions": "Obrada izmena",
    "Show on timeline": "Prikaži na vremenskoj liniji",
    "Open in map": "Otvori na karti",
    "Notifications": "Obaveštenja",
}
for key, expected in expected_frontend.items():
    assert frontend.get(key) == expected, (key, frontend.get(key))

catalogs = list(Path("/venv").rglob("sr/LC_MESSAGES/gramps.mo"))
assert catalogs, "Nije pronađen serverski Gramps sr katalog"

for catalog_path in catalogs:
    with catalog_path.open("rb") as stream:
        values = gettext.GNUTranslations(stream)._catalog.values()
    for value in values:
        if isinstance(value, str):
            assert not contains_cyrillic(value), catalog_path
        elif isinstance(value, (tuple, list)):
            for item in value:
                if isinstance(item, str):
                    assert not contains_cyrillic(item), catalog_path

print("BCS provjera odnosa i srpske latinice: uspješna")
