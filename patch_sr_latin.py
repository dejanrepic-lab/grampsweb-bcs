"""Pretvori Gramps Web izbor 'Srpski' u srpski na latinici."""

from __future__ import annotations

import json
import struct
import shutil
from io import BytesIO
from gettext import GNUTranslations
from pathlib import Path


MARKER = "GRAMPSWEB_BCS_SERBIAN_LATIN_UI_V1"
STATIC_LANG_DIR = Path("/app/static/lang")
FRONTEND_TRANSLATION = STATIC_LANG_DIR / "sr.json"
ENGLISH_TRANSLATION = STATIC_LANG_DIR / "en.json"
CROATIAN_TRANSLATION = STATIC_LANG_DIR / "hr.json"
MARKER_FILE = STATIC_LANG_DIR / ".grampsweb-bcs-serbian-latin-v1"

# Službeni srpski frontend prevod je znatno nepotpun. Ove dopune imaju
# prednost nad rezervnim hrvatskim prevodom i koriste srpsku latinicu,
# ekavicu i izraze koji su prirodni u Gramps Web sučelju.
FRONTEND_OVERRIDES = {
    "%s selected": "Izabrano: %s",
    "Accent color": "Boja naglaska",
    "Access the interactive API documentation": "Otvori interaktivnu API dokumentaciju",
    "Access token revoked": "Pristupni token je opozvan",
    "Access tokens": "Pristupni tokeni",
    "Account": "Nalog",
    "Add Family Member": "Dodaj člana porodice",
    "Add Participant": "Dodaj učesnika",
    "An error occurred": "Došlo je do greške",
    "Anniversary calendar subscription": "Pretplata na kalendar godišnjica",
    "App title": "Naslov aplikacije",
    "Appearance": "Izgled",
    "Applications and services can use persistent access tokens to access limited features of your account.": "Aplikacije i servisi mogu koristiti trajne pristupne tokene za ograničen pristup tvom nalogu.",
    "Assistant": "Asistent",
    "Base Map": "Osnovna karta",
    "Blog Post": "Objava na blogu",
    "Bookmark this": "Dodaj u obeleživače",
    "Change full name": "Promeni puno ime",
    "Change username": "Promeni korisničko ime",
    "Changes here affect all users of this tree.": "Ove izmene utiču na sve korisnike ovog stabla.",
    "Changes here only affect your account.": "Ove izmene utiču samo na tvoj nalog.",
    "Choose a name for your family tree. You can change this later.": "Izaberi naziv porodičnog stabla. Kasnije ga možeš promeniti.",
    "Clear selection": "Poništi izbor",
    "Colors, branding, and visual appearance": "Boje, oznake i vizuelni izgled",
    "Confirm Import": "Potvrdi uvoz",
    "Confirm Restore from Backup": "Potvrdi vraćanje sigurnosne kopije",
    "Coordinates": "Koordinate",
    "Creating your first tree": "Pravljenje prvog porodičnog stabla",
    "Customization": "Prilagođavanje",
    "Database checks, repairs, and other operations": "Provere baze, popravke i druge radnje",
    "Default family tree view": "Podrazumevani prikaz porodičnog stabla",
    "Delete %s objects?": "Obrisati %s objekata?",
    "Display preferences saved on this device": "Postavke prikaza sačuvane na ovom uređaju",
    "Draw a selection": "Nacrtaj oblast izbora",
    "Edit enclosing place": "Uredi nadređeno mesto",
    "Edit repository reference": "Uredi vezu sa repozitorijumom",
    "Enclosed places": "Obuhvaćena mesta",
    "End date is required": "Završni datum je obavezan",
    "End date must be after start date": "Završni datum mora biti posle početnog",
    "Exact place": "Tačno mesto",
    "Exactly two objects must be selected to perform a merge.": "Za spajanje moraju biti izabrana tačno dva objekta.",
    "Export media": "Izvezi medije",
    "Export/Import settings": "Postavke izvoza i uvoza",
    "External": "Spoljno",
    "External Search": "Spoljna pretraga",
    "External search failed": "Spoljna pretraga nije uspela",
    "Failed to fetch the Blog tag": "Učitavanje oznake Blog nije uspelo",
    "Failed to update": "Ažuriranje nije uspelo",
    "Failed to upload": "Otpremanje nije uspelo",
    "Fetching event record...": "Učitavanje zapisa događaja...",
    "Fetching family record...": "Učitavanje zapisa porodice...",
    "Fetching person record...": "Učitavanje zapisa osobe...",
    "Fetching place record...": "Učitavanje zapisa mesta...",
    "Filtering events...": "Filtriranje događaja...",
    "Filtering families...": "Filtriranje porodica...",
    "Filtering people in family tree...": "Filtriranje osoba u porodičnom stablu...",
    "Forum": "Forum",
    "Given Name First": "Prvo ime",
    "Hide unchanged fields": "Sakrij neizmenjena polja",
    "Historical Map": "Istorijska karta",
    "If set, overrides the family tree name in the title bar": "Ako je postavljeno, zameniće naziv porodičnog stabla u naslovnoj traci",
    "Import tree settings": "Uvezi postavke stabla",
    "Invalid date": "Neispravan datum",
    "Irreversible operations on tree data": "Nepovratne radnje nad podacima stabla",
    "Length": "Dužina",
    "Light": "Svetla",
    "Link to enclosing place": "Poveži sa nadređenim mestom",
    "Loading...": "Učitavanje...",
    "Manage and rebuild the search index": "Upravljaj indeksom pretrage i ponovo ga izgradi",
    "Max Degree of Separation": "Najveći stepen udaljenosti",
    "Max Number of Images displayed": "Najveći broj prikazanih slika",
    "Merge": "Spoji",
    "My Family Tree": "Moje porodično stablo",
    "Name your first tree": "Imenuj prvo porodično stablo",
    "New Blog Post": "Nova objava na blogu",
    "No active access tokens.": "Nema aktivnih pristupnih tokena.",
    "No changes detected.": "Nisu pronađene izmene.",
    "No coordinates": "Nema koordinata",
    "No issues found": "Nisu pronađeni problemi",
    "No objects found in this file.": "U ovom fajlu nisu pronađeni objekti.",
    "No objects selected.": "Nijedan objekat nije izabran.",
    "Not private": "Nije privatno",
    "Notifications": "Obaveštenja",
    "Object Type": "Vrsta objekta",
    "Open in map": "Otvori na karti",
    "Partner 1": "Prvi partner",
    "Partner 2": "Drugi partner",
    "Paternal Lineage": "Očeva loza",
    "Pick on map": "Izaberi na karti",
    "Please sign in again to continue.": "Za nastavak se ponovo prijavi.",
    "Preview Import": "Pregled uvoza",
    "Preview Restore": "Pregled vraćanja",
    "Preview Restore from Backup": "Pregled vraćanja sigurnosne kopije",
    "Primary color": "Glavna boja",
    "Process transactions": "Obrada izmena",
    "Processing your query...": "Obrada upita...",
    "Profile info, credentials, and account security": "Podaci profila, prijava i bezbednost naloga",
    "Quotas, imports, media, and storage management": "Kvote, uvoz, mediji i upravljanje prostorom",
    "Recently browsed": "Nedavno pregledano",
    "Recently changed": "Nedavno izmenjeno",
    "Remove bookmark": "Ukloni obeleživač",
    "Reset the tree to match an uploaded Gramps XML backup, adding, updating, and deleting objects as needed. This is a destructive replace, not a merge.": "Vrati stablo prema otpremljenoj Gramps XML sigurnosnoj kopiji, uz dodavanje, ažuriranje i brisanje objekata po potrebi. Ovo je potpuna zamena, a ne spajanje.",
    "Researcher Information": "Podaci o istraživaču",
    "Restore": "Vrati",
    "Restore from Backup": "Vrati iz sigurnosne kopije",
    "Retry": "Pokušaj ponovo",
    "Revoke": "Opozovi",
    "Revoke access token?": "Opozvati pristupni token?",
    "Revoking this token will immediately stop any application or service using it.": "Opozivanje tokena odmah će zaustaviti svaku aplikaciju ili servis koji ga koristi.",
    "Revision History": "Istorija revizija",
    "Running tasks": "Aktivni zadaci",
    "Save as Note": "Sačuvaj kao belešku",
    "Scope": "Opseg",
    "Search index": "Indeks pretrage",
    "Searching genealogy database...": "Pretraga genealoške baze...",
    "Select date": "Izaberi datum",
    "Select files": "Izaberi fajlove",
    "Settings successfully imported": "Postavke su uspešno uvezene",
    "Severity": "Nivo problema",
    "Show in tree": "Prikaži u stablu",
    "Show on timeline": "Prikaži na vremenskoj liniji",
    "Show unchanged fields": "Prikaži neizmenjena polja",
    "Some access tokens could not be loaded.": "Neki pristupni tokeni nisu mogli biti učitani.",
    "Surname First": "Prvo prezime",
    "System": "Sistem",
    "Task failed": "Zadatak nije uspeo",
    "The semantic search index is out of date. A full reindex is required.": "Indeks semantičke pretrage je zastareo. Potrebna je potpuna ponovna izgradnja.",
    "Theme colors": "Boje teme",
    "This file contains the following objects, which will be added to your tree:": "Ovaj fajl sadrži sledeće objekte koji će biti dodati u stablo:",
    "This restores object data and media references only. Binary media files and tree metadata (default person, bookmarks, name groups) are not affected.": "Ovim se vraćaju samo podaci objekata i veze prema medijima. Binarni medijski fajlovi i metapodaci stabla (osnovna osoba, obeleživači i grupe imena) neće biti promenjeni.",
    "This will permanently delete %s existing objects that are not present in the backup.": "Ovim će trajno biti obrisano %s postojećih objekata kojih nema u sigurnosnoj kopiji.",
    "Too many requests. Please try again later.": "Previše zahteva. Pokušaj ponovo kasnije.",
    "Tree Information": "Podaci o stablu",
    "Tree name": "Naziv stabla",
    "Tree name and researcher information": "Naziv stabla i podaci o istraživaču",
    "Tree settings": "Postavke stabla",
    "Unchanged": "Neizmenjeno",
    "Unsaved changes restored": "Nesačuvane izmene su vraćene",
    "Waiting for an administrator to set up your family tree.": "Čeka se da administrator podesi porodično stablo.",
    "Zoom in": "Uvećaj",
    "Zoom in to see event details": "Uvećaj za prikaz detalja događaja",
    "Zoom out": "Umanji",
    "issues found": "pronađenih problema",
}

LOWER = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "ђ": "đ",
    "е": "e",
    "ж": "ž",
    "з": "z",
    "и": "i",
    "ј": "j",
    "к": "k",
    "л": "l",
    "љ": "lj",
    "м": "m",
    "н": "n",
    "њ": "nj",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "ћ": "ć",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "c",
    "ч": "č",
    "џ": "dž",
    "ш": "š",
}

UPPER = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Ђ": "Đ",
    "Е": "E",
    "Ж": "Ž",
    "З": "Z",
    "И": "I",
    "Ј": "J",
    "К": "K",
    "Л": "L",
    "Љ": "Lj",
    "М": "M",
    "Н": "N",
    "Њ": "Nj",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "Ћ": "Ć",
    "У": "U",
    "Ф": "F",
    "Х": "H",
    "Ц": "C",
    "Ч": "Č",
    "Џ": "Dž",
    "Ш": "Š",
}

UPPER_DIGRAPHS = {"Љ": "LJ", "Њ": "NJ", "Џ": "DŽ"}


def transliterate(text: str) -> str:
    result: list[str] = []
    for index, character in enumerate(text):
        if character in LOWER:
            result.append(LOWER[character])
        elif character in UPPER_DIGRAPHS:
            next_is_upper = index + 1 < len(text) and text[index + 1].isupper()
            result.append(UPPER_DIGRAPHS[character] if next_is_upper else UPPER[character])
        else:
            result.append(UPPER.get(character, character))
    return "".join(result)


def transliterate_values(value):
    if isinstance(value, str):
        return transliterate(value)
    if isinstance(value, list):
        return [transliterate_values(item) for item in value]
    if isinstance(value, dict):
        return {key: transliterate_values(item) for key, item in value.items()}
    return value


def merge_frontend_translations(
    serbian: dict[str, object],
    english: dict[str, object],
    croatian: dict[str, object],
) -> tuple[dict[str, object], int, int, list[str]]:
    """Dopuni nepotpuni srpski prevod bez zamjene postojećih srpskih unosa."""

    merged = transliterate_values(serbian)
    from_overrides = 0
    from_croatian = 0

    for key, english_value in english.items():
        current_value = merged.get(key)
        untranslated = key not in merged or current_value == english_value
        if not untranslated:
            continue

        if key in FRONTEND_OVERRIDES:
            merged[key] = FRONTEND_OVERRIDES[key]
            from_overrides += 1
            continue

        croatian_value = croatian.get(key)
        if croatian_value is not None and croatian_value != english_value:
            merged[key] = croatian_value
            from_croatian += 1

    # Naše izabrane formulacije imaju prednost čak i kada službeni srpski
    # prevod kasnije dobije drugačiju, ali manje prirodnu varijantu.
    for key, value in FRONTEND_OVERRIDES.items():
        if key in english:
            merged[key] = value

    remaining_english = sorted(
        key for key, english_value in english.items() if merged.get(key) == english_value
    )
    return merged, from_overrides, from_croatian, remaining_english


def patch_frontend() -> None:
    if not FRONTEND_TRANSLATION.is_file():
        raise RuntimeError(f"Nije pronađen frontend prevod: {FRONTEND_TRANSLATION}")

    if not ENGLISH_TRANSLATION.is_file():
        raise RuntimeError(f"Nije pronađen engleski frontend: {ENGLISH_TRANSLATION}")

    serbian = json.loads(FRONTEND_TRANSLATION.read_text(encoding="utf-8"))
    english = json.loads(ENGLISH_TRANSLATION.read_text(encoding="utf-8"))
    croatian = (
        json.loads(CROATIAN_TRANSLATION.read_text(encoding="utf-8"))
        if CROATIAN_TRANSLATION.is_file()
        else {}
    )
    latin, from_overrides, from_croatian, remaining_english = (
        merge_frontend_translations(serbian, english, croatian)
    )
    rendered = json.dumps(latin, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    if any("\u0400" <= character <= "\u052f" for character in rendered):
        raise RuntimeError("U srpskom frontend prevodu je ostao ćirilični tekst")

    FRONTEND_TRANSLATION.write_text(rendered, encoding="utf-8")
    print(
        "Srpski frontend pretvoren u latinicu i dopunjen: "
        f"{FRONTEND_TRANSLATION} "
        f"(naše dopune: {from_overrides}, BCS rezerva: {from_croatian}, "
        f"preostalo engleskih unosa: {len(remaining_english)})"
    )


SEARCH_ROOTS = [Path("/venv"), Path("/usr/local"), Path("/usr"), Path("/app")]
APP_BACKEND_ROOTS = [Path("/venv"), Path("/usr/local"), Path("/app")]
LATIN_LOCALE_NAMES = ("sr_Latn", "sr@latin", "sr_RS@latin", "sr-Latn")


def find_message_dirs(
    locale_names: tuple[str, ...], roots: list[Path] | None = None
) -> list[Path]:
    found: set[Path] = set()
    for root in roots or SEARCH_ROOTS:
        if not root.exists():
            continue
        for locale_name in locale_names:
            for candidate in root.rglob(locale_name):
                messages = candidate / "LC_MESSAGES"
                if messages.is_dir() and any(messages.glob("*.mo")):
                    found.add(messages.resolve())
    return sorted(found)


def transliterate_mo(path: Path) -> None:
    data = path.read_bytes()
    if data[:4] == b"\xde\x12\x04\x95":
        endian = "<"
    elif data[:4] == b"\x95\x04\x12\xde":
        endian = ">"
    else:
        raise RuntimeError(f"Neispravan gettext katalog: {path}")

    if len(data) < 28:
        raise RuntimeError(f"Prekratak gettext katalog: {path}")

    _, _, count, original_table, translated_table, _, _ = struct.unpack_from(
        f"{endian}7I", data, 0
    )

    def read_messages(table_offset: int) -> list[bytes]:
        if table_offset + count * 8 > len(data):
            raise RuntimeError(f"Oštećena gettext tabela: {path}")
        messages: list[bytes] = []
        for index in range(count):
            length, offset = struct.unpack_from(
                f"{endian}2I", data, table_offset + index * 8
            )
            if offset + length > len(data):
                raise RuntimeError(f"Oštećena gettext poruka: {path}")
            messages.append(data[offset : offset + length])
        return messages

    originals = read_messages(original_table)
    translations = []
    for message in read_messages(translated_table):
        try:
            translations.append(transliterate(message.decode("utf-8")).encode("utf-8"))
        except UnicodeDecodeError as error:
            raise RuntimeError(f"Gettext katalog nije UTF-8: {path}") from error

    header_size = 7 * 4
    new_original_table = header_size
    new_translated_table = new_original_table + count * 8
    original_pool_offset = new_translated_table + count * 8

    original_pool = bytearray()
    original_entries: list[tuple[int, int]] = []
    for message in originals:
        original_entries.append((len(message), original_pool_offset + len(original_pool)))
        original_pool.extend(message)
        original_pool.append(0)

    translated_pool_offset = original_pool_offset + len(original_pool)
    translated_pool = bytearray()
    translated_entries: list[tuple[int, int]] = []
    for message in translations:
        translated_entries.append((len(message), translated_pool_offset + len(translated_pool)))
        translated_pool.extend(message)
        translated_pool.append(0)

    output = bytearray(
        struct.pack(
            f"{endian}7I",
            0x950412DE,
            0,
            count,
            new_original_table,
            new_translated_table,
            0,
            translated_pool_offset + len(translated_pool),
        )
    )
    for entry in original_entries:
        output.extend(struct.pack(f"{endian}2I", *entry))
    for entry in translated_entries:
        output.extend(struct.pack(f"{endian}2I", *entry))
    output.extend(original_pool)
    output.extend(translated_pool)

    # GNUTranslations provjera otkriva neispravan rezultat prije izmjene imagea.
    GNUTranslations(BytesIO(output))
    path.write_bytes(output)


def patch_backend() -> tuple[int, str]:
    copied = 0
    latin_message_dirs = find_message_dirs(LATIN_LOCALE_NAMES)

    for latin_messages in latin_message_dirs:
        locale_root = latin_messages.parent.parent
        serbian_messages = locale_root / "sr" / "LC_MESSAGES"
        serbian_messages.mkdir(parents=True, exist_ok=True)
        for source in latin_messages.glob("*.mo"):
            shutil.copy2(source, serbian_messages / source.name)
            copied += 1

    # Neki Gramps katalozi nemaju odgovarajući sr_Latn, pa i nakon kopiranja
    # službenih kataloga mogu ostati na ćirilici. Zato uvijek normalizujemo sve
    # aplikacijske sr kataloge; sistemski prevodi iz /usr nisu dio web sučelja.
    converted = 0
    for messages in find_message_dirs(("sr",), APP_BACKEND_ROOTS):
        for catalog in messages.glob("*.mo"):
            transliterate_mo(catalog)
            converted += 1

    if converted:
        print(
            "Srpski Gramps backend normalizovan na latinicu: "
            f"{converted} kataloga (službenih latinica kataloga kopirano: {copied})"
        )
        mode = "official-latin-plus-normalized-sr" if copied else "transliterated-sr"
        return converted, mode

    if copied:
        print(f"Službeni srpski latinica backend aktiviran: {copied} kataloga")
        return copied, "official-latin"

    # Frontend i BCS kalkulator odnosa i dalje rade. Ne prekidaj cijeli siguran
    # update ako buduća slika uopšte više ne sadrži serverski sr katalog.
    print("Serverski srpski gettext katalog nije pronađen; frontend latinica ostaje aktivna")
    return 0, "frontend-only"


def main() -> None:
    patch_frontend()
    copied, backend_mode = patch_backend()
    MARKER_FILE.write_text(
        f"{MARKER}\ngettext_catalogs={copied}\nbackend_mode={backend_mode}\n",
        encoding="utf-8",
    )
    print(f"BCS srpska latinica uspješno ugrađena: {MARKER_FILE}")


if __name__ == "__main__":
    main()
