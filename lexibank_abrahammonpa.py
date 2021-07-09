from collections import defaultdict
from pathlib import Path

import attr
import pylexibank
from clldutils.misc import slug


@attr.s
class CustomLanguage(pylexibank.Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Sino-Tibetan")
    Source_ID = attr.ib(default=None)
    WiktionaryName = attr.ib(default=None)
    Area = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "abrahammonpa"
    language_class = CustomLanguage
    form_spec = pylexibank.FormSpec(missing_data=("–", "-"))

    def cmd_makecldf(self, args):
        data = []
        for f in ["monpa.tsv", "khobwa.tsv", "hruso.tsv"]:
            data.extend(self.raw_dir.read_csv(f, delimiter="\t", dicts=True))
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english), lookup_factory="Name"
        )
        language_lookup = args.writer.add_languages(lookup_factory="WiktionaryName")
        args.writer.add_sources()
        missing = defaultdict(int)
        for c, entry in pylexibank.progressbar(enumerate(data), desc="cldfify", total=len(data)):
            if "" in entry.keys():
                if entry[""] in concept_lookup.keys():
                    for language, lid in language_lookup.items():
                        if language in entry.keys():
                            args.writer.add_forms_from_value(
                                Language_ID=lid,
                                Parameter_ID=concept_lookup[entry[""]],
                                Value=entry[language],
                                Source=["Abraham2018"],
                            )
                else:
                    missing[entry[""]] += 1
            elif "Gloss" in entry.keys():
                if entry["Gloss"] in concept_lookup.keys():
                    for language, lid in language_lookup.items():
                        if language in entry.keys():
                            args.writer.add_forms_from_value(
                                Language_ID=lid,
                                Parameter_ID=concept_lookup[entry["Gloss"]],
                                Value=entry[language],
                                Source=["Abraham2018"],
                            )
