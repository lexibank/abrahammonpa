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
        languages, concepts = [], {}
        missing = defaultdict(int)
        with self.cldf as ds:
            for concept in self.concepts:
                ds.add_concept(
                        ID=concept['NUMBER'],
                        Name=concept['ENGLISH'],
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS']
                        )
                concepts[concept['ENGLISH']] = concept['ID']
            for language in self.languages:
                if language['Language_in_Wiktionary']:
                    ds.add_language(
                            ID=slug(language['Language']),
                            Glottocode=language['Glottolog'],
                            Name=language['Language']
                            )
                languages.append((language['Language_in_Wiktionary'])

            ds.add_sources(*self.raw.read_bib())
            for entry in tqdm(data, desc='cldfify the data'):
                if entry[''] not in concepts:
                    missing[entry['']] +=1
                else:
                    for langauge in languages:
                        value = self.lexemes.get(entry[language],
                            entry[language]
                            )
                        if value.strip():
                            ds.add_lexemes(
                                Language_ID=languages[language],
                                Parameter_ID=concepts[concept],
                                Value=self.lexemes.get(value, value),
                                Source=['Abrahammonpa2018']
                                )
            for i, m in enumerate(missing):
                print(str(i+1)+'\t'+m)



