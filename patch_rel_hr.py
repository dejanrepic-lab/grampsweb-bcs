"""Dopuni ugrađeni Gramps hrvatski kalkulator pojedinačnih srodstava."""

from pathlib import Path

import gramps.plugins.rel.rel_hr as rel_hr


MARKER = "GRAMPSWEB_BCS_SINGLE_RELATIONSHIPS_V4"
REGISTRY_MARKER = "GRAMPSWEB_BCS_SERBIAN_RELATIONSHIP_LOCALES_V4"
METHODS = r'''
    # GRAMPSWEB_BCS_SINGLE_RELATIONSHIPS_V4
    @staticmethod
    def _bcs_term(gender, male, female, unknown):
        from gramps.gen.lib import Person

        if gender == Person.MALE:
            return male
        if gender == Person.FEMALE:
            return female
        return unknown

    @staticmethod
    def _bcs_cousin_term(number, gender):
        from gramps.gen.lib import Person

        male = {
            1: "prvi rođak",
            2: "drugi rođak",
            3: "treći rođak",
            4: "četvrti rođak",
            5: "peti rođak",
            6: "šesti rođak",
            7: "sedmi rođak",
            8: "osmi rođak",
            9: "deveti rođak",
            10: "deseti rođak",
        }
        female = {
            1: "prva rodica",
            2: "druga rodica",
            3: "treća rodica",
            4: "četvrta rodica",
            5: "peta rodica",
            6: "šesta rodica",
            7: "sedma rodica",
            8: "osma rodica",
            9: "deveta rodica",
            10: "deseta rodica",
        }
        if gender == Person.MALE:
            return male.get(number, "rođak %d. reda" % number)
        if gender == Person.FEMALE:
            return female.get(number, "rodica %d. reda" % number)
        return "rođak ili rodica %d. reda" % number

    def _bcs_first_cousin_term(self, gender, path_a, path_b):
        """Prvi rođak osobe A: brat/sestra od strica, ujaka ili tetke."""
        parent_a = path_a[:1].lower()
        parent_b = path_b[:1].lower()
        if parent_b == "m":
            relation = "tetke"
        elif parent_b == "f" and parent_a == "f":
            relation = "strica"
        elif parent_b == "f" and parent_a == "m":
            relation = "ujaka"
        else:
            return self._bcs_cousin_term(1, gender)
        return self._bcs_term(
            gender,
            "brat od %s" % relation,
            "sestra od %s" % relation,
            "brat/sestra od %s" % relation,
        )

    @staticmethod
    def _bcs_cousin_genitive(number, parent_code):
        male = {
            1: "prvog rođaka",
            2: "drugog rođaka",
            3: "trećeg rođaka",
            4: "četvrtog rođaka",
            5: "petog rođaka",
            6: "šestog rođaka",
            7: "sedmog rođaka",
            8: "osmog rođaka",
            9: "devetog rođaka",
            10: "desetog rođaka",
        }
        female = {
            1: "prve rodice",
            2: "druge rodice",
            3: "treće rodice",
            4: "četvrte rodice",
            5: "pete rodice",
            6: "šeste rodice",
            7: "sedme rodice",
            8: "osme rodice",
            9: "devete rodice",
            10: "desete rodice",
        }
        if parent_code == "f":
            return male.get(number, "rođaka %d. reda" % number)
        if parent_code == "m":
            return female.get(number, "rodice %d. reda" % number)
        return "rođaka ili rodice %d. reda" % number

    @staticmethod
    def _bcs_ancestor_genitive(path, level):
        """Predak u genitivu, sa očevom ili majčinom granom stabla."""
        names = {
            2: ("djeda", "bake", "djeda ili bake"),
            3: ("pradjeda", "prabake", "pradjeda ili prabake"),
            4: ("čukundjeda", "čukunbake", "čukundjeda ili čukunbake"),
        }
        normalized = path.lower()
        side = (
            "po ocu"
            if normalized[:1] == "f"
            else "po majci"
            if normalized[:1] == "m"
            else ""
        )
        if level in names:
            gender_code = normalized[level - 1 : level]
            if gender_code == "f":
                ancestor = names[level][0]
            elif gender_code == "m":
                ancestor = names[level][1]
            else:
                ancestor = names[level][2]
        else:
            ancestor = "pretka u %d. generaciji" % level
        return "%s %s" % (ancestor, side) if side else ancestor

    @staticmethod
    def _bcs_generation_count(number):
        if number == 1:
            return "jednu generaciju"
        if number % 10 in (2, 3, 4) and number % 100 not in (12, 13, 14):
            return "%d generacije" % number
        return "%d generacija" % number

    @staticmethod
    def _bcs_qualify(term, only_birth=True, in_law=False):
        if not only_birth:
            term = "nebiološko srodstvo: " + term
        if in_law:
            term += " (po braku)"
        return term

    def get_single_relationship_string(
        self,
        Ga,
        Gb,
        gender_a,
        gender_b,
        reltocommon_a="",
        reltocommon_b="",
        only_birth=True,
        in_law_a=False,
        in_law_b=False,
    ):
        """Vrati razumljiv BCS naziv odnosa osobe B prema osobi A."""
        in_law = in_law_a or in_law_b

        if Ga == 0 and Gb == 0:
            return "ista osoba"

        if Ga == 0:
            direct = {
                1: ("sin", "ćerka", "dijete"),
                2: ("unuk", "unuka", "unuče"),
                3: ("praunuk", "praunuka", "praunuče"),
                4: ("čukununuk", "čukununuka", "čukununuče"),
            }
            if Gb in direct:
                term = self._bcs_term(gender_b, *direct[Gb])
            else:
                term = self._bcs_term(
                    gender_b,
                    "muški potomak u %d. generaciji" % Gb,
                    "ženski potomak u %d. generaciji" % Gb,
                    "potomak u %d. generaciji" % Gb,
                )
            return self._bcs_qualify(term, only_birth, in_law)

        if Gb == 0:
            direct = {
                1: ("otac", "majka", "roditelj"),
                2: ("djed", "baka", "djed/baka"),
                3: ("pradjed", "prabaka", "pradjed/prabaka"),
                4: ("čukundjed", "čukunbaka", "čukundjed/čukunbaka"),
            }
            if Ga in direct:
                term = self._bcs_term(gender_b, *direct[Ga])
            else:
                term = self._bcs_term(
                    gender_b,
                    "muški predak u %d. generaciji" % Ga,
                    "ženski predak u %d. generaciji" % Ga,
                    "predak u %d. generaciji" % Ga,
                )
            return self._bcs_qualify(term, only_birth, in_law)

        if Gb == 1:
            if Ga == 1:
                term = self._bcs_term(gender_b, "brat", "sestra", "brat/sestra")
            elif Ga == 2:
                side = reltocommon_a[:1].lower()
                male = "stric" if side == "f" else "ujak" if side == "m" else "stric/ujak"
                term = self._bcs_term(gender_b, male, "tetka", "stric/ujak/tetka")
            elif Ga >= 3:
                ancestor = self._bcs_ancestor_genitive(reltocommon_a, Ga - 1)
                term = self._bcs_term(
                    gender_b,
                    "brat %s" % ancestor,
                    "sestra %s" % ancestor,
                    "brat ili sestra %s" % ancestor,
                )
            return self._bcs_qualify(term, only_birth, in_law)

        if Ga == 1:
            if Gb == 2:
                from gramps.gen.lib import Person

                sibling = reltocommon_b[:1].lower()
                if sibling == "m":
                    term = self._bcs_term(
                        gender_b, "sestrić", "sestričina", "sestrić/sestričina"
                    )
                elif sibling == "f" and gender_a == Person.FEMALE:
                    term = self._bcs_term(
                        gender_b, "bratanac", "bratanica", "bratanac/bratanica"
                    )
                elif sibling == "f":
                    term = self._bcs_term(
                        gender_b, "sinovac", "sinovica", "sinovac/sinovica"
                    )
                else:
                    term = self._bcs_term(
                        gender_b, "nećak", "nećaka", "nećak/nećaka"
                    )
            elif Gb == 3:
                term = self._bcs_term(
                    gender_b, "pranećak", "pranećakinja", "pranećak/pranećakinja"
                )
            else:
                term = self._bcs_term(
                    gender_b,
                    "muški potomak brata/sestre u %d. generaciji" % (Gb - 1),
                    "ženski potomak brata/sestre u %d. generaciji" % (Gb - 1),
                    "potomak brata/sestre u %d. generaciji" % (Gb - 1),
                )
            return self._bcs_qualify(term, only_birth, in_law)

        degree = min(Ga, Gb) - 1
        difference = abs(Ga - Gb)

        if difference == 0:
            if degree == 1:
                term = self._bcs_first_cousin_term(
                    gender_b, reltocommon_a, reltocommon_b
                )
            else:
                term = self._bcs_cousin_term(degree, gender_b)
        elif Ga > Gb:
            # Osoba B je u starijoj grani: npr. očeva prva rodica.
            cousin = self._bcs_cousin_term(degree, gender_b)
            if difference == 1:
                from gramps.gen.lib import Person

                side = reltocommon_a[:1].lower()
                if side == "f":
                    if gender_b == Person.MALE:
                        term = "očev %s" % cousin
                    elif gender_b == Person.FEMALE:
                        term = "očeva %s" % cousin
                    else:
                        term = "%s oca" % cousin
                elif side == "m":
                    if gender_b == Person.MALE:
                        term = "majčin %s" % cousin
                    elif gender_b == Person.FEMALE:
                        term = "majčina %s" % cousin
                    else:
                        term = "%s majke" % cousin
                else:
                    term = "%s jednog od roditelja" % cousin
            elif difference == 2:
                owner = self._bcs_ancestor_genitive(reltocommon_a, 2)
                term = "%s %s" % (cousin, owner)
            else:
                term = "%s pretka, %s iznad" % (
                    cousin,
                    self._bcs_generation_count(difference),
                )
        else:
            # Osoba B je potomak rođaka/rodice osobe A.
            parent_code = reltocommon_b[:1].lower()
            parent = self._bcs_cousin_genitive(degree, parent_code)
            descendants = {
                1: ("sin", "ćerka", "dijete"),
                2: ("unuk", "unuka", "unuče"),
                3: ("praunuk", "praunuka", "praunuče"),
            }
            if difference in descendants:
                descendant = self._bcs_term(gender_b, *descendants[difference])
                term = "%s %s" % (descendant, parent)
            else:
                term = "potomak %s, %s ispod" % (
                    parent,
                    self._bcs_generation_count(difference),
                )
        return self._bcs_qualify(term, only_birth, in_law)

    def get_sibling_relationship_string(
        self, sib_type, gender_a, gender_b, in_law_a=False, in_law_b=False
    ):
        if sib_type in (self.NORM_SIB, self.UNKNOWN_SIB):
            term = self._bcs_term(gender_b, "brat", "sestra", "brat/sestra")
        elif sib_type in (self.HALF_SIB_MOTHER, self.HALF_SIB_FATHER):
            term = self._bcs_term(gender_b, "polubrat", "polusestra", "polubrat/polusestra")
        else:
            term = self._bcs_term(
                gender_b,
                "brat po očuhu ili maćehi",
                "sestra po očuhu ili maćehi",
                "brat/sestra po očuhu ili maćehi",
            )
        if in_law_a or in_law_b:
            term += " (po braku)"
        return term

    def get_partner_relationship_string(self, spouse_type, gender_a, gender_b):
        former = {
            self.PARTNER_EX_MARRIED,
            self.PARTNER_EX_UNMARRIED,
            self.PARTNER_EX_CIVIL_UNION,
            self.PARTNER_EX_UNKNOWN_REL,
        }
        if spouse_type == self.PARTNER_MARRIED:
            return self._bcs_term(gender_b, "suprug", "supruga", "supružnik")
        if spouse_type == self.PARTNER_EX_MARRIED:
            return self._bcs_term(
                gender_b, "bivši suprug", "bivša supruga", "bivši supružnik"
            )
        if spouse_type in former:
            return self._bcs_term(
                gender_b, "bivši partner", "bivša partnerica", "bivši partner/partnerica"
            )
        if spouse_type:
            return self._bcs_term(gender_b, "partner", "partnerica", "partner/partnerica")
        return ""

'''


def main() -> None:
    target = Path(rel_hr.__file__)
    source = target.read_text(encoding="utf-8")
    if MARKER not in source:
        needle = "    def get_plural_relationship_string(\n"
        if needle not in source:
            raise RuntimeError(f"Nije pronađeno očekivano mjesto u {target}")
        target.write_text(source.replace(needle, METHODS + needle, 1), encoding="utf-8")
        print(f"BCS zakrpa uspješno dodana: {target}")
    else:
        print(f"BCS zakrpa je već prisutna: {target}")

    registry = target.with_name("relplugins.gpr.py")
    registry_source = registry.read_text(encoding="utf-8")
    if REGISTRY_MARKER not in registry_source:
        plugin_start = registry_source.find('plg.id = "relcalc_hr"')
        list_start = registry_source.find("plg.lang_list = [", plugin_start)
        list_end = registry_source.find("]", list_start)
        if plugin_start < 0 or list_start < 0 or list_end < 0:
            raise RuntimeError(f"Nije pronađena registracija hrvatskog kalkulatora u {registry}")
        serbian_locales = f'''    # {REGISTRY_MARKER}
    "sr",
    "sr_RS",
    "sr_RS.UTF-8",
    "sr_RS.utf-8",
    "sr_RS.utf8",
    "sr@latin",
    "sr_RS@latin",
    "sr_RS.UTF-8@latin",
    "sr_Latn",
    "sr-Latn",
'''
        registry_source = (
            registry_source[:list_end] + serbian_locales + registry_source[list_end:]
        )
        registry.write_text(registry_source, encoding="utf-8")
        print(f"Srpski jezik povezan s BCS kalkulatorom: {registry}")
    else:
        print(f"Srpski jezik je već povezan s BCS kalkulatorom: {registry}")


if __name__ == "__main__":
    main()

