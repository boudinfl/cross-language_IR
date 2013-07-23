#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Name:
    hmm_segmenter.py

:Authors:
    Florian Boudin (florian.boudin@univ-nantes.fr)

:Date:
    22 july 2013 (creation)

:Description:
    A HMM Japanese segmenter.
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

    if len(argv) != 3:
        print "Usage : hmm_segmenter.py training_file test_file output_file"
        sys.exit()

    train_set = content_handler(argv[0])
    test_set = content_handler(argv[1])

    model = train(train_set.sentences)

    handle = codecs.open(argv[2], 'w', 'utf-8')
    handle.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    handle.write('<dataset>\n')
    for i in range(len(test_set.raw_sentences)):
        segmented_sentence = word_segmentation(model, test_set.raw_sentences[i])
        handle.write('\t<sentence sid="'+str(i)+'">\n')
        handle.write('\t\t<raw>'+segmented_sentence+'</raw>\n')
        handle.write('\t</sentence>\n')
    handle.write('</dataset>')
    handle.close()

################################################################################


################################################################################
# Useful functions
################################################################################
def add_one(dic, value):
    if not dic.has_key(value):
        dic[value] = 0.0
    dic[value] += 1.0
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

        elif tag == 'raw':
            self.raw_sentences.append(self.buffer)

        # Flush the buffer
        self.buffer = ''
    #-B-----------------------------------------------------------------------B-
################################################################################



################################################################################
# Training function
################################################################################
def train(sentences):

    observation_prob = {}
    state_trans_prob = {}

    # Iterates through the sentences
    for sentence in sentences:

        for i in range(len(sentence)):
            sentence[i] = 'c'.join(sentence[i])
        annotated_sequence = 'b'.join(sentence)

        previous_state = ''
        current_state = ''

        for i in range(0, len(annotated_sequence)-1, 2):
            observation = annotated_sequence[i:i+3]
            bigram = observation[0]+observation[2]
            current_state = observation[1]

            if not observation_prob.has_key(bigram):
                observation_prob[bigram] = {'c': 0.0, 'b': 0.0}
            observation_prob[bigram][current_state] += 1.0

            if previous_state != '':
                add_one(state_trans_prob, (previous_state, current_state))
            previous_state = current_state

    # Normalize observation probabilities
    for bigram in observation_prob:
        norm_factor = observation_prob[bigram]['c'] \
                      + observation_prob[bigram]['b']
        observation_prob[bigram]['c'] /= norm_factor
        observation_prob[bigram]['b'] /= norm_factor

    # Normalize transition probabilities
    norm_factor = 0.0
    for t in state_trans_prob:
        norm_factor += state_trans_prob[t]
    for t in state_trans_prob:
        state_trans_prob[t] /= norm_factor
    
    return [observation_prob, state_trans_prob]
################################################################################


################################################################################
# Function for word segmentation
################################################################################
def word_segmentation(model, sentence):

    observation_prob = model[0]
    state_trans_prob = model[1]

    unseen_prob = 0.01

    observations = []
    lattice = []

    for i in range(len(sentence)-1):
        bigram = sentence[i:i+2]
        observations.append(bigram)

        if observation_prob.has_key(bigram):
            lattice.append(observation_prob[bigram])
            lattice[-1]['c'] = max(unseen_prob, lattice[-1]['c'])
            lattice[-1]['b'] = max(unseen_prob, lattice[-1]['b'])
        else:
            lattice.append({'c': unseen_prob, 'b': unseen_prob})

    # Use viterbi to decode the lattice

    # Initialisation
    V = []
    bisect.insort(V, (lattice[0]['c'], ['c']))
    bisect.insort(V, (lattice[0]['b'], ['b']))

    # Looping the observations
    for i in range(1, len(observations)):

        # Select the n-best paths
        best_V = []
        best_V.append(V[-1])
        highest_prob = best_V[0][0]
        for j in range(len(V)-2,-1,-1):
            if V[j][0] >= highest_prob:
                best_V.append(V[j])
            else:
                break

        new_V = []
        for prob, stack in best_V:

            # Compute probability for continuation
            prob_c = prob * lattice[i]['c'] * state_trans_prob[(stack[-1], 'c')]
            bisect.insort(new_V, (prob_c, stack+['c']))
            prob_b = prob * lattice[i]['b'] * state_trans_prob[(stack[-1], 'b')]
            bisect.insort(new_V, (prob_b, stack+['b']))

        V = list(new_V)

    best_V = V[-1][1]

    # Sentence segmentation 
    segmented_sentence = []
    for i in range(len(sentence)-1):
        if best_V[i] == 'c':
            segmented_sentence.append(sentence[i])
        else:
            segmented_sentence.append(sentence[i]+" ")
    segmented_sentence.append(sentence[-1])
    return ''.join(segmented_sentence)


################################################################################

################################################################################
# To launch the script 
################################################################################
if __name__ == "__main__":
    main(sys.argv[1:])
################################################################################