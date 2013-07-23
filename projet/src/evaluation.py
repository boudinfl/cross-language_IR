#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    evaluation.py

:Authors:
    Florian Boudin (florian.boudin@univ-nantes.fr)

:Date:
    22 july 2013 (creation)

:Description:
    Evaluation a Japanese segmentation.
"""

import re
import sys
import xml.sax
import codecs
import bisect


################################################################################
# Main function handling function calls
################################################################################
def main(argv):

    if len(argv) != 2:
        print "Usage : evaluation.py system_file reference_file"
        sys.exit()

    system_set = content_handler(argv[0])
    reference_set = content_handler(argv[1])

    precisions = []
    recalls = []

    for i in range(len(system_set.raw_sentences)):

        if system_set.sid[i] != reference_set.sid[i]:
            print "Sentence identifiers are not the same"
            sys.exit()

        system_sentence = system_set.raw_sentences[i].split(' ')
        reference_sentence = reference_set.raw_sentences[i].split(' ')


        for j in range(len(system_sentence)):
            system_sentence[j] = 'c'.join(system_sentence[j])
        annotated_system_sentence = 'b'.join(system_sentence)

        for j in range(len(reference_sentence)):
            reference_sentence[j] = 'c'.join(reference_sentence[j])
        annotated_reference_sentence = 'b'.join(reference_sentence)

        number_of_boundaries_detected = 0.0
        number_of_boundaries_to_find = 0.0
        number_of_correct_boundaries = 0.0

        for j in range(1, len(annotated_system_sentence), 2):

            if annotated_system_sentence[j] == 'b':
                number_of_boundaries_detected += 1.0
                if annotated_reference_sentence[j] == 'b':
                    number_of_correct_boundaries += 1.0
            if annotated_reference_sentence[j] == 'b':
                number_of_boundaries_to_find += 1.0

        if number_of_boundaries_detected != 0:
            precisions.append(number_of_correct_boundaries/number_of_boundaries_detected)
        if number_of_boundaries_to_find != 0:
            recalls.append(number_of_correct_boundaries/number_of_boundaries_to_find)


    # Compute average precision and recall
    avg_p = sum(precisions)/len(precisions)
    avg_r = sum(recalls)/len(recalls)
    avg_f = (2.0 * (avg_r*avg_p)) / (avg_r + avg_p)
    print 'Avg Precision', avg_p
    print 'Avg Recall', avg_r
    print 'Avg f-measure', avg_f


################################################################################


################################################################################
# XML Sax Parser for KNBC xml file
################################################################################
class content_handler(xml.sax.ContentHandler):
    #-T-----------------------------------------------------------------------T-
    def __init__(self, path):
        # Tree for pushing/poping tags, attrs
        self.tree = []
        
        # Buffer for xml element
        self.buffer = ''

        # Container for the sentence list
        self.sentences = []
        self.current_sentence = []
        self.raw_sentences = []
        self.sid = []

        # Construct and launch the parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(path)
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def startElement(self, name, attrs):
        self.tree.append((name, attrs))
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def characters(self, data):
        self.buffer += data.strip()
    #-B-----------------------------------------------------------------------B-
        
    #-T-----------------------------------------------------------------------T-
    def endElement(self, name):
        tag, attrs = self.tree.pop()

        if tag == 'token':
            self.current_sentence.append(self.buffer)

        elif tag == 'sentence':
            self.sentences.append(self.current_sentence)
            self.current_sentence = []
            self.sid.append(attrs['sid'])

        elif tag == 'raw':
            self.raw_sentences.append(re.sub('\s+', ' ', self.buffer))

        # Flush the buffer
        self.buffer = ''
    #-B-----------------------------------------------------------------------B-
################################################################################


################################################################################
# To launch the script 
################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
################################################################################