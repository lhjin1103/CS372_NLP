import nltk
import csv
from nltk.classify import MaxentClassifier
from nltk.corpus import names
from nltk.parse.corenlp import CoreNLPParser
from nltk import Tree
from nltk.tree import ParentedTree
import json

parser = CoreNLPParser()

def preprocess(line):
    tid = line[0]
    text = line[1]
    pronoun = line[2]
    pronoun_offset = line[3]
    a_name = line[4]
    a_offset = line[5]
    a_coref = line[6]
    b_name = line[7]
    b_offset = line[8]
    b_coref = line[9]
    url = line[10]   

    ptree = str(parse(text))
    return tid, ptree, pronoun, pronoun_offset, a_name, a_offset, a_coref, b_name, b_offset, b_coref, url

def parse(text):
    return next(parser.raw_parse(text))

if __name__ == '__main__':
    '''
    dev_file = open("gap-development.tsv", 'r', encoding='utf-8')
    dev_read_file = csv.reader(dev_file, delimiter="\t")
    dev_set = []
    for line in dev_read_file:
        dev_set.append(line)
    dev_set = dev_set[1:]

    dev_processed = {}
    for line in dev_set:
        try:
            line = preprocess(line)
        except:
            print(line)
            continue
        tid = line[0]
        dev_processed[tid] = line[1:]

    with open('devleopment.json', 'w') as dev_file:
        json.dump(dev_processed, dev_file, ensure_ascii=False)

    val_file = open("gap-validation.tsv", 'r', encoding='utf-8')
    val_read_file = csv.reader(val_file, delimiter="\t")
    val_set = []
    for line in val_read_file:
        val_set.append(line)
    val_set = val_set[1:]

    val_processed = {}
    for line in val_set:
        try:
            line = preprocess(line)
        except:
            print(line)
            continue
        tid = line[0]
        val_processed[tid] = line[1:]

    with open('validation.json', 'w') as val_file:
        json.dump(val_processed, val_file, ensure_ascii=False)
    '''

    test_file = open("gap-test.tsv", 'r', encoding='utf-8')
    test_read_file = csv.reader(test_file, delimiter="\t")
    test_set = []
    for line in test_read_file:
        test_set.append(line)
    test_set = test_set[1:]

    test_processed = {}
    for line in test_set:
        try:
            line = preprocess(line)
        except:
            print(line)
            continue
        tid = line[0]
        test_processed[tid] = line[1:]

    with open('test.json', 'w') as test_file:
        json.dump(test_processed, test_file, ensure_ascii=False)


    