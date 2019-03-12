import re
import csv
import lingpy

import requests
from bs4 import BeautifulSoup

wp = requests.get('https://en.wiktionary.org/wiki/Appendix:Hrusish_comparative_vocabulary_lists')
soup = BeautifulSoup(wp.content, "html.parser")

language_table_header, language_table =[],[]
languages = soup.findAll("table", {'class': 'wikitable sortable'})[1]
for lh in languages.findAll('th'):
    language_table_header.append(lh.get_text().rstrip('\n'))

for r in languages.findAll("tr"):
    temp = []
    for cell in r.findAll('td'):
        temp.append(cell.get_text().rstrip('\n'))
    language_table.append(temp)

language_table =[x for x in language_table if x!=[]]
vob_table_header, vob_table =[], []
vob = soup.findAll("table", {'class' : 'wikitable sortable'})[2]
for vh in vob.findAll('th'):
    vob_table_header.append(vh.get_text().rstrip('\n'))

for v in vob.findAll('tr'):
    vtemp = []
    for vcell in v.findAll('td'):
        vtemp.append(vcell.get_text().rstrip('\n'))
    vob_table.append(vtemp)

vob_table =[x for x in vob_table if x!=[]]

with open('raw/Hruso_languages.csv','w',newline='') as lw:
    languagewriter = csv.writer(lw, delimiter=',', quotechar='"')
    languagewriter.writerow(language_table_header)
    languagewriter.writerows(language_table)
    lw.close()

with open('raw/hruso.tsv','w',newline='') as vw:
    vocabwriter = csv.writer(vw, delimiter='\t', quotechar='"')
    vocabwriter.writerow(vob_table_header)
    vocabwriter.writerows(vob_table)
    vw.close()
