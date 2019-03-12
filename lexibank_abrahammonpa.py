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

import requests
from bs4 import BeautifulSoup


class Dataset(NonSplittingDataset):
    dir = Path(__file__).parent
    id = "abrahammonpa"

    def cmd_download(self, **kw):
        wp = requests.get('https://en.wiktionary.org/wiki/Appendix:Hrusish_comparative_vocabulary_lists')
        soup = BeautifulSoup(wp.content, "html.parser")

        language_table_header, language_table =[],[]
        languages = soup.findAll("table", {'class': 'wikitable sortable'})[0]
        for lh in languages.findAll('th'):
            language_table_header.append(lh.get_text().rstrip('\n'))

        for r in languages.findAll("tr"):
            temp = []
            for cell in r.findAll('td'):
                temp.append(cell.get_text().rstrip('\n'))
            language_table.append(temp)

        language_table =[x for x in language_table if x!=[]]

        vob_table_header, vob_table =[], []
        vob = soup.findAll("table", {'class' : 'wikitable sortable'})[1]
        for vh in vob.findAll('th'):
            vob_table_header.append(vh.get_text().rstrip('\n'))

        for v in vob.findAll('tr'):
            vtemp = []
            for vcell in v.findAll('td'):
                vtemp.append(vcell.get_text().rstrip('\n'))
            vob_table.append(vtemp)

        vob_table =[x for x in vob_table if x!=[]]

        with open(self.dir.joinpath('raw', 'hruso_languages.csv').as_posix(),'w',newline='') as lw:
            languagewriter = csv.writer(lw, delimiter=',', quotechar='"')
            languagewriter.writerow(language_table_header)
            languagewriter.writerows(language_table)
            lw.close()

        with open(self.dir.joinpath('raw', 'hruso.tsv').as_posix(),'w',newline='') as vw:
            vocabwriter = csv.writer(vw, delimiter='\t', quotechar='"')
            vocabwriter.writerow(vob_table_header)
            vocabwriter.writerows(vob_table)
            vw.close()
            
    def clean_form(self, item, form):
        if form not in ['*', '---', '']:
            return split_text(strip_brackets(form), ',;/||')[0]

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.
        """
        # read in and merge
        data =[]
        for i in ['monpa.tsv','khobwa.tsv', 'hruso.tsv']:
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
                if '' in entry.keys():
                    if entry[''] in concepts.keys():
                        for language in check_languages:
                            if language in entry.keys():
                                value = self.lexemes.get(entry[language],
                                    entry[language]
                                    )
                                if not (value.strip()==None or value.strip()=='–'):
                                    ds.add_lexemes(
                                        Language_ID=slug(language),
                                        Parameter_ID=concepts[entry['']],
                                        Value=value,
                                        Source=['Abraham2018']
                                        )
                    else:
                        missing[entry['']] +=1
                elif 'Gloss' in entry.keys():
                    if entry['Gloss'] in concepts.keys():
                        for language in check_languages:
                            if language in entry.keys():
                                value = self.lexemes.get(entry[language],
                                    entry[language]
                                    )
                                if not (value.strip()==None or value.strip()=='–'):
                                    ds.add_lexemes(
                                        Language_ID=slug(language),
                                        Parameter_ID=concepts[entry['Gloss']],
                                        Value=value,
                                        Source=['Abraham2018']
                                        )


