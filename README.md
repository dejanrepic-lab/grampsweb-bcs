# Gramps Web BCS

Nezvanična Gramps Web Docker slika sa srpskim prevodom na latinici i prirodnijim BCS nazivima srodstva.

Slika se gradi direktno na posljednjoj službenoj slici `ghcr.io/gramps-project/grampsweb:latest`. Ne mijenja podatke porodičnog stabla.

## Šta dopunjava

- izbor jezika **Srpski** prikazuje latinicu i srpska imena mjeseci (`januar`, `februar`, `mart`...);
- dopunjava nedostajuće Gramps Web prevode, bez miješanja latinice i ćirilice;
- dodaje prirodnije nazive srodstva kao što su `stric`, `ujak`, `tetka`, `prvi rođak` i `druga rodica`;
- isti dopunjeni kalkulator srodstva ostaje dostupan i korisnicima hrvatskog jezika.

## Gotova Docker slika

```text
ghcr.io/dejanrepic-lab/grampsweb-bcs:latest
```

GitHub Actions svaki dan provjerava službenu Gramps Web sliku. Nova BCS slika se gradi samo kada se promijeni službena slika ili sadržaj ovog repozitorija. Izgradnja se prekida ako automatska provjera pronađe ćirilicu, nedostajući prevod ili nekompatibilnu zakrpu.

Objavljena slika sadrži SBOM i BuildKit provenance podatke. Workflow koristi samo ugrađeni `GITHUB_TOKEN`, sa minimalnim dozvolama `contents: read` i `packages: write`; nema privatnih ključeva ni ličnih podataka.

## Jednokratna ZimaOS instalacija

Preuzmi instalacijski skript, pa ga pokreni:

```bash
curl -fsSLo /tmp/install-grampsweb-bcs.sh \
  https://raw.githubusercontent.com/dejanrepic-lab/grampsweb-bcs/main/install-zimaos.sh

sudo bash /tmp/install-grampsweb-bcs.sh
```

Instalacija:

1. pronalazi postojeći Gramps Web compose stack;
2. preuzima i provjerava gotovu javnu Docker sliku;
3. čuva kopiju compose fajla;
4. mijenja samo dvije Gramps Web image linije;
5. pravi backup baze i korisnika;
6. ponovo pokreće Gramps Web i provjerava da je zdrav;
7. uključuje sedmični updater sa automatskim rollbackom.

Nakon ove jednokratne migracije više nisu potrebni ZIP-ovi, kopiranje patch fajlova ni lokalni `docker build`.

Ako compose stack nije na standardnom mjestu, putanju možeš navesti ovako:

```bash
sudo GRAMPSWEB_COMPOSE_DIR=/putanja/do/stacka \
  bash /tmp/install-grampsweb-bcs.sh
```

## Ažuriranje i provjera na ZimaOS-u

Automatska provjera radi nedjeljom oko 04:30. Prije zamjene slike updater zaustavlja samo Gramps Web i Celery, zatim čuva konzistentan backup baze i korisnika u:

```text
/DATA/Backups/grampsweb-auto-update
```

Čuva posljednjih pet automatskih kopija. Ako nova verzija ne prođe provjeru ili se Gramps ne pokrene kao zdrav, prethodna slika se automatski vraća.

Ručna provjera i eventualno ažuriranje:

```bash
sudo systemctl start grampsweb-bcs-update.service
```

Posljednjih 100 redova dnevnika:

```bash
sudo journalctl -u grampsweb-bcs-update.service -n 100 --no-pager
```

Sljedeći zakazani termin:

```bash
sudo systemctl list-timers grampsweb-bcs-update.timer --no-pager
```

Provjera same slike bez mijenjanja aktivnih kontejnera:

```bash
sudo /usr/local/lib/grampsweb-bcs/update-grampsweb-bcs.sh --check-only
```

## Ručna Docker upotreba

U servisima `grampsweb` i `grampsweb_celery` koristi:

```yaml
image: ghcr.io/dejanrepic-lab/grampsweb-bcs:latest
pull_policy: never
environment:
  LANGUAGE: sr
```

`pull_policy: never` je namjeran: provjereni updater prvo preuzima i testira sliku, pa tek onda ponovo pravi kontejnere.

## Razvoj

Lokalna izgradnja:

```bash
docker build --pull -t grampsweb-bcs:test .
docker run --rm --entrypoint python3 grampsweb-bcs:test \
  /usr/local/lib/grampsweb-bcs/verify_image.py
```

## Licenca

GPL-3.0-or-later. Gramps i Gramps Web su zasebni projekti svojih autora. Ovaj repozitorij nije službeni Gramps projekat.
