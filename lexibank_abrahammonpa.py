# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.path import Path
from pylexibank.dataset import NonSplittingDataset
from clldutils.misc import slug
from clldutils.text import split_text, strip_brackets

from tqdm import tqdm
from collections import defaultdict

import re
import csv
import lingpy


class Dataset(NonSplittingDataset):
    dir = Path(__file__).parent
    id = "abrahammonpa"

    def cmd_download(self, **kw):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw`, e.g.

        >>> self.raw.download(url, fname)
        """
        pass

    def clean_form(self, item, form):
        if form not in ['*', '---', '']:
            return split_text(strip_brackets(form), ',;/')[0]

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.
        """
        # read in and merge
        data =[]
        for i in ['monpa.tsv','khobwa.tsv']:
            with open(self.dir.joinpath('raw',i).as_posix(),'r') as csvfile:
                reader=csv.DictReader(csvfile, delimiter='\t')
                temp = [row for row in reader]
            data.extend(temp)

        # build cldf
        check_languages, concepts = [], {}
        with self.cldf as ds:
            for concept in self.concepts:
                ds.add_concept(
                        ID=concept['NUMBER'],
                        Name=concept['ENGLISH'],
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS']
                        )
                concepts[concept['ENGLISH']] = concept['NUMBER']
            for language in self.languages:
                if language['Language_in_Wiktionary'] !='':
                    ds.add_language(
                            ID=slug(language['Language_in_Wiktionary']),
                            Glottocode=language['Glottolog'],
                            Name=language['Language_in_Wiktionary']
                            )
                    check_languages.append(language['Language_in_Wiktionary'])

            ds.add_sources(*self.raw.read_bib())
            missing = defaultdict(int)
            for c, entry in tqdm(enumerate(data), desc='cldfify the data'):
                if entry[''] in concepts.keys():
                    for language in check_languages:
                        if language in entry.keys():
                            value = self.lexemes.get(entry[language],
                                entry[language]
                                )
                            form = value.split(',')[0].strip()
                            segments=[s for s in form]
                            if value.strip():
                                ds.add_lexemes(
                                    Language_ID=slug(language),
                                    Parameter_ID=concepts[entry['']],
                                    Value=value,
                                    Form=form,
                                    Segments=segments,
                                    Source=['Abraham2018']
                                    )
                else:
                    missing[entry['']] +=1


