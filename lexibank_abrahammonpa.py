import csv
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets, split_text_with_context
from pylexibank.dataset import Dataset as BaseDataset 
from pylexibank.dataset import Language
from pylexibank.util import pb
import attr


@attr.s
class HLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default='Sino-Tibetan')
    Source_ID = attr.ib(default=None)
    WiktionaryName = attr.ib(default=None)
    Area = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "abrahammonpa"
    language_class = HLanguage

    def cmd_download(self, **kw):
        wp = requests.get(
            "https://en.wiktionary.org/wiki/Appendix:Hrusish_comparative_vocabulary_lists"
        )
        soup = BeautifulSoup(wp.content, "html.parser")

        language_table_header, language_table = [], []
        languages = soup.findAll("table", {"class": "wikitable sortable"})[1]
        for lh in languages.findAll("th"):
            language_table_header.append(lh.get_text().rstrip("\n"))

        for r in languages.findAll("tr"):
            temp = []
            for cell in r.findAll("td"):
                temp.append(cell.get_text().rstrip("\n"))
            language_table.append(temp)

        language_table = [x for x in language_table if x != []]
        vob_table_header, vob_table = [], []
        vob = soup.findAll("table", {"class": "wikitable sortable"})[2]
        for vh in vob.findAll("th"):
            vob_table_header.append(vh.get_text().rstrip("\n"))

        for v in vob.findAll("tr"):
            vtemp = []
            for vcell in v.findAll("td"):
                vtemp.append(vcell.get_text().rstrip("\n"))
            vob_table.append(vtemp)

        vob_table = [x for x in vob_table if x != []]

        with open("raw/hruso_languages.csv", "w", newline="") as lw:
            languagewriter = csv.writer(lw, delimiter=",", quotechar='"')
            languagewriter.writerow(language_table_header)
            languagewriter.writerows(language_table)
            lw.close()

        with open("raw/hruso.tsv", "w", newline="") as vw:
            vocabwriter = csv.writer(vw, delimiter="\t", quotechar='"')
            vocabwriter.writerow(vob_table_header)
            vocabwriter.writerows(vob_table)
            vw.close()

    def clean_form(self, item, form):
        if form not in ["–"]:
            return strip_brackets(form)

    def split_forms(self, item, value):
        if value in self.lexemes:  # pragma: no cover
            self.log.info('overriding via lexemes.csv: %r -> %r' % (value, self.lexemes[value]))
        value = self.lexemes.get(value, value)
        return [self.clean_form(item, form)
                for form in split_text_with_context(value, separators=';')]

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.
        """
        # read in and merge
        data = []
        for i in ["monpa.tsv", "khobwa.tsv", "hruso.tsv"]:
            with open(self.dir.joinpath("raw", i).as_posix(), "r") as csvfile:
                reader = csv.DictReader(csvfile, delimiter="\t")
                temp = [row for row in reader]
            data.extend(temp)

        # build cldf
        concepts = {}
        with self.cldf as ds:
            ds.add_concepts(id_factory=lambda c: c.number)
            concepts = {c.english: c.number for c in self.conceptlist.concepts.values()}
            ds.add_languages()
            check_languages = {k['WiktionaryName']: k['ID'] for k in
                    self.languages}

            ds.add_sources(*self.raw.read_bib())
            missing = defaultdict(int)

            for c, entry in pb(enumerate(data), desc="cldfify", total=len(data)):
                if "" in entry.keys():
                    if entry[""] in concepts.keys():
                        for language, lid in check_languages.items():
                            if language in entry.keys():
                                ds.add_lexemes(
                                    Language_ID=lid,
                                    Parameter_ID=concepts[entry[""]],
                                    Value=entry[language],
                                    Source=["Abraham2018"],
                                )
                    else:
                        missing[entry[""]] += 1
                elif "Gloss" in entry.keys():
                    if entry["Gloss"] in concepts.keys():
                        for language, lid in check_languages.items():
                            if language in entry.keys():
                                ds.add_lexemes(
                                    Language_ID=lid,
                                    Parameter_ID=concepts[entry["Gloss"]],
                                    Value=entry[language],
                                    Source=["Abraham2018"],
                                )
