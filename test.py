<<<<<<< HEAD
# coding: utf-8
from __future__ import unicode_literals
from lingpy import *
from lexibank_abrahammonpa import Dataset

wl = Wordlist.from_cldf(Dataset().cldf_dir.joinpath('cldf-metadata.json'))

=======
>>>>>>> 755919caf231a387d70930ba16ac21f1c56f2096
def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)
