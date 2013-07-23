#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
	knbc_to_xml.py

:Authors:
    Florian Boudin (florian.boudin@univ-nantes.fr)

:Date:
    22 july 2013 (creation)

:Description:
	A script that creates a word segmentation dataset for Japanese in xml format
	from the Kyoto-University and NTT Blog Corpus (KNBC).
"""

import re
import sys
import codecs

import nltk
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader.util import find_corpus_fileids
from nltk.data import FileSystemPathPointer
from nltk.corpus.reader.knbc import KNBCorpusReader


################################################################################
def main(argv):

	if len(argv) != 3:
		print "Usage : knbc_to_xml.py train_file test_file reference_file"
		sys.exit()

	read_knbc(argv[0], argv[1], argv[2])
################################################################################


################################################################################
def _knbc_fileids_sort(x):
	cells = x.split('-')
	return (cells[0], int(cells[1]), int(cells[2]), int(cells[3]))
################################################################################

################################################################################
def write_train(sentences, output_file):

	handle = codecs.open(output_file, 'w', 'utf-8')
	handle.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	handle.write('<dataset>\n')
	for i in range(len(sentences)):
		sentence = sentences[i]
		handle.write('\t<sentence sid="'+str(i)+'">\n')
		handle.write('\t\t<raw>'+''.join(sentence)+'</raw>\n')
		handle.write('\t\t<tokens>\n')
		for j in range(len(sentence)):
			handle.write('\t\t\t<token tid="'+str(j)+'">'+sentence[j]+'</token>\n')
		handle.write('\t\t</tokens>\n')
		handle.write('\t</sentence>\n')
	handle.write('</dataset>')
	handle.close()

################################################################################

################################################################################
def write_test(sentences, output_file):

	handle = codecs.open(output_file, 'w', 'utf-8')
	handle.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	handle.write('<dataset>\n')
	for i in range(len(sentences)):
		sentence = sentences[i]
		handle.write('\t<sentence sid="'+str(i)+'">\n')
		handle.write('\t\t<raw>'+''.join(sentence)+'</raw>\n')
		handle.write('\t</sentence>\n')
	handle.write('</dataset>')
	handle.close()

################################################################################

################################################################################
def write_reference(sentences, output_file):

	handle = codecs.open(output_file, 'w', 'utf-8')
	handle.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	handle.write('<dataset>\n')
	for i in range(len(sentences)):
		sentence = sentences[i]
		handle.write('\t<sentence sid="'+str(i)+'">\n')
		handle.write('\t\t<raw>'+' '.join(sentence)+'</raw>\n')
		handle.write('\t</sentence>\n')
	handle.write('</dataset>')
	handle.close()

################################################################################

################################################################################
def read_knbc(train_file, test_file, reference_file):

	root = nltk.data.find('corpora/knbc/corpus1')
	fileids = [f for f in find_corpus_fileids(FileSystemPathPointer(root), ".*")
              if re.search(r"\d\-\d\-[\d]+\-[\d]+", f)]

	knbc = LazyCorpusLoader('knbc/corpus1', KNBCorpusReader,
           sorted(fileids, key=_knbc_fileids_sort), encoding='euc-jp')

	sentences = knbc.sents()

	write_train(sentences[0:4000], train_file)
	write_test(sentences[4000:-1], test_file)
	write_reference(sentences[4000:-1], reference_file)
################################################################################


################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
################################################################################