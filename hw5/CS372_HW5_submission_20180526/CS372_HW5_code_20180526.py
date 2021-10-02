import nltk
import csv
from nltk.classify import MaxentClassifier
from nltk.corpus import names
from nltk.parse.corenlp import CoreNLPParser
from nltk import Tree
from nltk.tree import ParentedTree
import json
from nltk import word_tokenize, pos_tag


#used in gender matching, but deleted in the final model
female_pronoun = ['she', 'her', 'hers']
male_pronoun = ['he', 'his', 'him']
male_names = [name for name in names.words('male.txt')]
female_names = [name for name in names.words('female.txt')]

#Parser used in this model _ Stanford CooreNLPParser
#You should connect to the server before using this parser
parser = CoreNLPParser()

def extract_page_feature_without_syntax(line):
    '''
    Used for extracting feature set: for the texts where Stanford CoreNLP makes error
    page: contains the url info
    see extract_page_feature(line) to find the detailed explanation
    '''
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
    a_name = a_name.split(' ')[0]
    b_name = b_name.split(' ')[0]
    features = {}
    features['pronoun'] = pronoun
    wordlist = word_tokenize(text)
    p_pos = find_pronoun(wordlist, pronoun, pronoun_offset)
    a_pos = find_name(wordlist, a_name, a_offset)
    b_pos = find_name(wordlist, b_name, b_offset)

    if p_pos!=0: 
        features['before'] = pos_tag([wordlist[p_pos-1]])[0][1]
    else:
        features['before'] = None

    if p_pos!=0: 
        features['after'] = pos_tag([wordlist[p_pos+1]])[0][1]
    else:
        features['after'] = None

    features['a_text_dist'] = p_pos - a_pos
    features['b_text_dist'] = p_pos - b_pos

    features['sentence_length'] = len(wordlist)
    features['a_count'] = count_occurence(text, a_name)
    features['b_count'] = count_occurence(text, b_name)

    try: features['a_page_count'] = page_count(tid, a_name)
    except: features['a_page_count'] = features['a_count']
    try: features['b_page_count'] = page_count(tid, b_name)
    except: features['b_page_count'] = features['b_count']
    answer = (a_coref, b_coref)

    return (features, answer)


def extract_page_features(line):
    '''
    Used for extracting feature set: for the texts where Stanford CoreNLP works -> has the parsed tree
    page: contains the url info
    '''
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

    a_name = a_name.split(' ')[0]   # use only the first name
    b_name = b_name.split(' ')[0]

    features = {}
    features['pronoun'] = pronoun   # minor feature: store the pronoun info
    
    features['uppercase'] = (pronoun.lower() == pronoun)    # minor feature: find out if it is the first word of the sentence

    a_text_dist, b_text_dist, a_tree_dist, b_tree_dist, before, after, a_con, b_con = process(line)
    features['a_text_dist'] = a_text_dist   # word distance between a and the pronoun
    features['b_text_dist'] = b_text_dist   # word distance between b and the pronoun
    features['a_tree_dist'] = a_tree_dist   # tree distance between a and the pronoun
    features['b_tree_dist'] = b_tree_dist   # tree distance between b and the pronoun
    features['a_con'] = a_con   # are a and the pronoun directly connected?
    features['b_con'] = b_con   # are b and the pronoun directly connected?
    
    # before & after -> used to find the class of the pronoun
    features['before'] = before # the POS just before the pronoun
    features['after'] = after   # the POS just after the pronoun

    features['sentence_length'] = len(Tree.fromstring(text).leaves())   #minor feature: sentence length

    raw_text = ' '.join(Tree.fromstring(text).leaves())
    features['a_count'] = count_occurence(raw_text, a_name) # occurence of a in the text
    features['b_count'] = count_occurence(raw_text, b_name) # occurence of b in the text

    try: features['a_page_count'] = page_count(tid, a_name) # occurence of a in the page
    except: features['a_page_count'] = features['a_count']
    try: features['b_page_count'] = page_count(tid, b_name) # occurence of b in the page
    except: features['b_page_count'] = features['b_count']
    answer = (a_coref, b_coref)

    return (features, answer)

def extract_snippet_feature_without_syntax(line):
    '''
    Used for extracting feature set: for the texts where Stanford CoreNLP makes an error
    snippet: does not contain the url info
    see extract_page_feature(line) to find the detailed explanation
    '''
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
    a_name = a_name.split(' ')[0]
    b_name = b_name.split(' ')[0]
    features = {}
    features['pronoun'] = pronoun
    wordlist = word_tokenize(text)
    p_pos = find_pronoun(wordlist, pronoun, pronoun_offset)
    a_pos = find_name(wordlist, a_name, a_offset)
    b_pos = find_name(wordlist, b_name, b_offset)

    if p_pos!=0: 
        features['before'] = pos_tag([wordlist[p_pos-1]])[0][1]
    else:
        features['before'] = None

    if p_pos!=0: 
        features['after'] = pos_tag([wordlist[p_pos+1]])[0][1]
    else:
        features['after'] = None

    features['a_text_dist'] = p_pos - a_pos
    features['b_text_dist'] = p_pos - b_pos

    features['sentence_length'] = len(wordlist)
    features['a_count'] = count_occurence(text, a_name)
    features['b_count'] = count_occurence(text, b_name)

    answer = (a_coref, b_coref)

    return (features, answer)

def extract_snippet_features(line):
    '''
    Used for extracting feature set: for the texts where Stanford CoreNLP works -> has the parsed tree
    snippet: does not contain the url info
    see extract_page_feature(line) to find the detailed explanation
    '''
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

    a_name = a_name.split(' ')[0]
    b_name = b_name.split(' ')[0]

    features = {}
    features['pronoun'] = pronoun
    
    features['uppercase'] = (pronoun.lower() == pronoun)

    a_text_dist, b_text_dist, a_tree_dist, b_tree_dist, before, after, a_con, b_con = process(line)
    features['a_text_dist'] = a_text_dist
    features['b_text_dist'] = b_text_dist
    features['a_tree_dist'] = a_tree_dist
    features['b_tree_dist'] = b_tree_dist
    features['a_con'] = a_con
    features['b_con'] = b_con
    
    features['before'] = before
    features['after'] = after

    features['sentence_length'] = len(Tree.fromstring(text).leaves())

    raw_text = ' '.join(Tree.fromstring(text).leaves())
    features['a_count'] = count_occurence(raw_text, a_name)
    features['b_count'] = count_occurence(raw_text, b_name)

    answer = (a_coref, b_coref)

    return (features, answer)

def name_gender(name):
    '''
    gender matching
    not used in the final model
    '''
    male = False
    female = False
    if name in female_names:
        female = True
    if name in male_names:
        male = True
    if female and not male: return 'F'
    if male and not female: return 'M'
    return 'N'

def process(line):
    '''
    finding the syntactic clues using the parsed tree
    '''
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

    #ptree = parse(text)
    ptree = Tree.fromstring(text)
    p_text_pos, pronoun_pos = find_pronoun_in_tree(ptree, pronoun, pronoun_offset)
    a_text_pos, a_name_pos = find_name_in_tree(ptree, a_name, a_offset)
    b_text_pos, b_name_pos = find_name_in_tree(ptree, b_name, b_offset)

    a_text_distance = p_text_pos - a_text_pos
    b_text_distance = p_text_pos - b_text_pos

    a_tree_distance = tree_distance(pronoun_pos, a_name_pos)
    b_tree_distance = tree_distance(pronoun_pos, b_name_pos)

    a_connection = direct_connection(ptree, pronoun_pos, a_name_pos)
    b_connection = direct_connection(ptree, pronoun_pos, b_name_pos)

    before, after = close(ptree, p_text_pos)

    return a_text_distance, b_text_distance, a_tree_distance, b_tree_distance, before, after, a_connection, b_connection

def parse(text):
    return next(parser.raw_parse(text))

def close(tree, text_pos):
    '''
    find the 'before' POS and 'after' POS
    '''
    word = tree.leaves()
    if text_pos == 0:
        before = None
    else: 
        index = text_pos-1
        tree_pos = tree.leaf_treeposition(index)
        before = tree[tree_pos[:-1]].label()

    if text_pos == len(word):
        after = None
    else:
        tree_pos = tree.leaf_treeposition(text_pos+1)
        after = tree[tree_pos[:-1]].label()
    return before, after
        


def find_pronoun(text, word, offset):
    '''
    returns the word number of the pronoun
    '''
    offset = int(offset)
    counter = 0
    for j, w in enumerate(text):
        counter += len(w) + 1
        if counter > offset:
            if word in w:
                return j
    return 0

def find_pronoun_in_tree(tree, pronoun, offset):
    '''
    returns the tree position of the pronoun
    '''    
    words = tree.leaves()
    index = find_pronoun(words, pronoun, offset)
    tree_location = tree.leaf_treeposition(index)
    return (index, tree_location)

def find_name(text, name, offset):
    '''
    returns the word number of the name
    '''
    offset = int(offset)
    counter = 0
    for j, w in enumerate(text):
        counter += len(w) + 1
        if counter > offset:
            if w in name:
                return j
    return 0

def find_name_in_tree(tree, name, offset):
    '''
    returns the tree position of the name
    '''
    words = tree.leaves()
    index = find_name(words, name, offset)
    tree_location = tree.leaf_treeposition(index)
    return (index, tree_location)

def count_occurence(text, name):
    return text.count(name)

def tree_distance(p_pos, n_pos):
    '''
    returns the tree distance between the pronoun and the name
    '''
    counter = 0
    while counter<min(len(p_pos), len(n_pos)):
        if p_pos[:counter] == n_pos[:counter]:
            counter += 1
        else: return len(p_pos) + len(n_pos) - counter
    return len(p_pos) + len(n_pos) - counter

def direct_connection(tree, p_pos, n_pos):
    '''
    does the pronoun and the name are directly connected in the tree?
    '''
    current_pos = p_pos[:-3]
    while tree[current_pos].label() != 'NP' and tree[current_pos].label() != 'S':
        current_pos = current_pos[:-1]
        if tree[current_pos].label() == 'ROOT': return False
    l = len(current_pos)
    if current_pos == n_pos[:l]:
        return True
    return False

def page_count(tid, name):
    '''
    get the word counts from the url
    '''
    if 'dev' in tid:
        f = dev_url
    else:
        f = test_url

    page = f[tid]
    return count_occurence(page, name)

def crawl(url):
    '''
    for url crawling
    '''
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser") 
    body = soup.select('#bodyContent')
    return(body[0].text)

def preprocess(line):
    '''
    for parsing using stanford corenlpparser
    '''
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



if __name__ == '__main__':
    
    dev_file = open("gap-development.tsv", 'r', encoding='utf-8')
    dev_read_file = csv.reader(dev_file, delimiter="\t")
    dev_pre_set = []
    for line in dev_read_file:
        dev_pre_set.append(line)
    dev_pre_set = dev_pre_set[1:]
    
    test_file = open("gap-test.tsv", 'r', encoding='utf-8')
    test_read_file = csv.reader(test_file, delimiter="\t")
    test_pre_set = []
    for line in test_read_file:
        test_pre_set.append(line)
    test_pre_set = test_pre_set[1:]

    ##################################### Parsing #################################################
    dev_data = {}
    for line in dev_pre_set:
        try:
            line = preprocess(line)
        except:
            print(line)
            continue
        tid = line[0]
        dev_data[tid] = line[1:]

    test_data = {}
    for line in test_pre_set:
        try:
            line = preprocess(line)
        except:
            print(line)
            continue
        tid = line[0]
        test_data[tid] = line[1:]

    '''
    with open('test.json', 'w') as test_file:
        json.dump(test_data, test_file, ensure_ascii=False)

    with open('devleopment.json', 'w') as dev_file:
        json.dump(dev_data, dev_file, ensure_ascii=False)    

    with open('devleopment.json') as json_file1:  
        dev_data = json.load(json_file1) 
    with open('test.json') as json_file:
        test_data = json.load(json_file)
    '''
    ##############################################################################################

    
    ################################### crawling wikipedia ########################################
    dev_url = {}
    for line in dev_pre_set:
        tid = line[0]
        url = line[10]
        try:
            dev_url[tid] = crawl(url)
        except: 
            print (tid, url)
    
    test_url = {}
    for line in test_pre_set:
        tid = line[0]
        url = line[10]
        try:
            test_url[tid] = crawl(url)
        except: 
            print (tid, url)

    '''
    with open('dev_url.json', 'w') as dev_file:
        json.dump(dev_url, dev_file, ensure_ascii=False)

    with open('test_url.json', 'w') as test_file:
        json.dump(test_url, test_file, ensure_ascii=False)

    with open('dev_url.json') as json_file:
        dev_url = json.load(json_file)
    with open('test_url.json') as json_file:
        test_url = json.load(json_file)
    '''

    ################################################################################################






    ##################################### Training & Making Output ##################################
    dev_set = []
    for key in dev_data:
        d = [key] + dev_data[key]
        dev_set.append(d)

    test_page_feature_set = []

    for i in range(2000):
        key = 'test-' + str(i+1)
        if key in test_data:
            v = [key] + test_data[key]
            test_page_feature_set.append(extract_page_features(v))
        else:
            test_page_feature_set.append(extract_page_feature_without_syntax(test_pre_set[i]))


    dev_page_feature_set = [extract_page_features(case) for case in dev_set]
    page_classifier = nltk.MaxentClassifier.train(dev_page_feature_set)

    f = open('CS372_HW5_page_output.tsv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f, delimiter='\t')

    for i in range(2000):
        f, a = test_page_feature_set[i]
        (a_coref, b_coref) = page_classifier.classify(f)
        tid = 'test-' + str(i+1)
        print(tid, a_coref, b_coref)
        wr.writerow([tid, a_coref, b_coref])

    test_snippet_feature_set = []

    for i in range(2000):
        key = 'test-' + str(i+1)
        if key in test_data:
            v = [key] + test_data[key]
            test_snippet_feature_set.append(extract_snippet_features(v))
        else:
            test_snippet_feature_set.append(extract_snippet_feature_without_syntax(test_pre_set[i]))


    dev_snippet_feature_set = [extract_snippet_features(case) for case in dev_set]
    snippet_classifier = nltk.MaxentClassifier.train(dev_snippet_feature_set)

    f = open('CS372_HW5_snippet_output.tsv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f, delimiter='\t')

    for i in range(2000):
        f, a = test_snippet_feature_set[i]
        (a_coref, b_coref) = snippet_classifier.classify(f)
        tid = 'test-' + str(i+1)
        print(tid, a_coref, b_coref)
        wr.writerow([tid, a_coref, b_coref])


    



    
    