import nltk
from nltk import pos_tag
from nltk import word_tokenize
from nltk.chunk import conlltags2tree, tree2conlltags, ne_chunk
import csv
from nltk.corpus import wordnet as wn
from nltk.tree import *

##target verbs : including various forms of selected verbs##
target = ['activate', 'activates', 'activated', 'inhibit', 'inhibits', 'inhibited', 'bind', 'bound', 'binds', 'stimulate', 'stimulated', 'stimulates', 'abolish', 'abolishes', 'abolished']

##pre-defined POS sets used to re-tag some ambiguous words. Many biological terms are replaced using wordnet, not here##
pre_defined = {'receptor': 'NN', 'behavior': 'NN', 'signaling': 'NN', 'multiple': 'JJ', 'sodium': 'NN', 'signalling': 'NN', 'statins': 'NN'}

##'discard' tokens used in phrase simplification: phrases following these tokens are simpley discarded during tree traversal##
delete = ['with', 'of', 'in', 'as']

correctset = []
##loading the sentence file, getting the sentences and the expected triples out##
def load():
    sents = []

    f = open("CS372_HW4_output_20180526.csv", "r")
    rdr = csv.reader(f)
    for line in rdr:
        sents.append(line[0])
        correctset.append(line[1])
    f.close()
    return sents

##re-tagging ambiguous words
def re_tag(sent):
    newsent = []
    for i, (word, pos) in enumerate(sent):
        out = True
        check = False
        for t in target: ##tagging target verbs into 'TV'
            if t == word:
                check = True
        if (pos=='JJ' or pos=='FW') and wn.synsets(word)==[]: pos = 'NN' ##re-tagging biological terms
        if check and out:
            newsent.append((word, 'TV'))
        elif (word == ('which') or word==('that')) and out:
            newsent.append((word, 'WHICH'))
        elif word ==',' and out:
            newsent.append((word, 'CC'))
        elif word == '(': ##for discarding the phrases inside ()
            out = False
        elif word == ')':
            out = True
        elif word =='I' and sent[i-1][0].lower() == 'type' and out:
            newsent.append((word, 'NN'))
        elif word.lower() in pre_defined and out:
            newpos = pre_defined[word.lower()]
            newsent.append((word, newpos))
        elif word == 'uptake' and sent[i-1][1] == 'JJ' and out:
            newsent.append((word, 'NN'))
        elif word == 'running' and not (sent[-1][0]).startswith('V') and out:
            newsent.append((word, 'NN'))
        else:
            if out:
                newsent.append((word, pos))
    return newsent  ##returning re-tagged sentences

def tag(sent):
    return pos_tag(word_tokenize(sent))
def chunk(parser, tagged_sent):
    return parser.parse(tagged_sent)      

def preprocess(sents):
    newlist = []
    for sent in sents:
        newlist.append(re_tag(tag(sent)))
    return newlist

def checktree(tsent):   ##find out the form of the target chunk and move to each case
    tree = chunk(cp, tsent)
    check = False
    for subtree in tree.subtrees():
        if subtree.label() == ('TARGET'):
            return annotatetarget(subtree)
        elif subtree.label() == ('ANDTARGET'):
            return annotateand(subtree)
        elif subtree.label() == ('THATTARGET'):
            return annotatethat(subtree)

def annotatetarget(tree):   #if annotated in 'TARGET
    t = ParentedTree.convert(tree)
    for subtree in t.subtrees():
        if subtree.label() == 'TVP': #find 'TVP' chunk
            action = subtree.leaves()
            newaction = []
            newleft = []
            newright = []
            for w in action:    #simplify, by removing MD, CC, and RB (modifiers)
                if w[1] == 'MD' or w[1]=='CC' or w[1]=='RB': None
                else: newaction.append(w[0])
            actionstring = (' '.join(newaction))
            try: lefttree = subtree.left_sibling().leaves() #find the left subtree, which will be 'A'
            except: lefttree = subtree.left_sibling()
            try: righttree = subtree.right_sibling().leaves() #find the right subtree, which will be 'B'
            except: righttree = subtree.right_sibling()
            for w in righttree: #simplify the right subtree and put into A
                if w[0] in delete: break
                if w[0]!= 'whereas' and w[1]!= 'DT':
                    newright.append(w[0])
            for w in lefttree:  #simplify the left subtree and put into B
                if w[0] in delete: break
                if w[1]!= 'DT':
                    newleft.append(w[0])

            leftstring = (' '. join(newleft))
            rightstring = (' '. join(newright))
    return ('<' + leftstring + ', ' + actionstring + ', ' + rightstring + '>') #return the triple

def annotateand(tree): #ANDTARGET
    newaction = []
    newleft = []
    newright = []

    t = ParentedTree.convert(tree)
    for subtree in t.subtrees():    #find the leftmost N* phrase
        if subtree.label().startswith('N'):
            lefttree= subtree.leaves()
            break
    for w in lefttree:      #simplify the left subtree
        #if w[0] in delete: break
        if w[1]!= 'DT':
            newleft.append(w[0])
    
    for subtree in t.subtrees():
        if subtree.label() == 'ANDT':   #find the ANDT chunk
            for stree in subtree.subtrees():
                if stree.label() == 'TVP': #find TVP chunk inside the ANDT chunk
                    action = stree.leaves()
                    for w in action:    #simplify
                        if w[1] == 'MD' or w[1]=='CC' or w[1]=='RB': None
                        else: newaction.append(w[0])
                    try: righttree = stree.right_sibling().leaves() #find B
                    except: righttree = stree.right_sibling()
                    for w in righttree: #simplify
                        # if w[0] in delete: break
                        if w[0]!= 'whereas' and w[1]!= 'DT':
                            newright.append(w[0])

    actionstring = ' '.join(newaction)
    leftstring = ' '.join(newleft)
    rightstring = ' '.join(newright)
    return ('<' + leftstring + ', ' + actionstring + ', ' + rightstring + '>') 

def annotatethat(tree): #THATTARGET
    newaction = []
    newleft = []
    newright = []

    t = ParentedTree.convert(tree)
    for subtree in t.subtrees():
        if subtree.label().startswith('N'): #find the leftmost N* phrase
            lefttree= subtree.leaves()
            break
    for w in lefttree:
        #if w[0] in delete: break
        if w[1]!= 'DT': #siimplify the left tree
            newleft.append(w[0])

    for subtree in t.subtrees():
        if subtree.label() == 'THATT': #find THATT chunk
            for stree in subtree.subtrees():
                if stree.label() == 'TVP': #find TVP chunk inside
                    action = stree.leaves()
                    for w in action: #simiplify
                        if w[1] == 'MD' or w[1]=='CC' or w[1]=='RB': None
                        else: newaction.append(w[0])
                    try: righttree = stree.right_sibling().leaves() #find B
                    except: righttree = stree.right_sibling()
                    for w in righttree:
                        #if w[0] in delete: break
                        if w[0]!= 'whereas' and w[1]!= 'DT': #simplify
                            newright.append(w[0])       

    actionstring = ' '.join(newaction)
    leftstring = ' '.join(newleft)
    rightstring = ' '.join(newright)
    return ('<' + leftstring + ', ' + actionstring + ', ' + rightstring + '>') 

grammar = r"""
    JJ: {<RB><JJ><JJ>*}
    NP: {<PRP.|DT|PP\$>?<JJ.?>*<FW>*<NN.?>+}   # chunk determiner/possessive, adjectives and noun
        {<NP><JJ>}
        {<NNP>+}                # chunk sequences of proper nouns
        {<NP><CC><NP>}
        {<RB>*<VBN>*<NNS>}
        {<VB.>?<NP>(<IN><NP>)+} #{<VBG> + <VBN>}
        {<NP>(<C.*>+<NP>)+<C.*>?}
        {<PRP>}
        {<NP><VBN><IN>}
        {<JJ><CC><NP>}
        {<NP><RB><CC><IN><NP>}
        {<VBG><NP>}
        {<NP><CC><JJ><IN><NP>} #ex) metabolic inputs, such as amino acids
        {<RB><RB><NP><CC><RB><NP>} #ex) not only a but also b
    RB: {<RB><CC><RB>}

    TARGET: {<NP.?><TVP><NP.?>} #TARGET Chunk
    TVP: {<VBP><TV><IN>}    #Target Verb Phrase, including various forms of possible verbs and their modifiers
        {<RB|VB.?|MD>*<TV><IN>}
        {<VBP><TV><IN>}
        {<RB|VB.?|MD>*<TV><RB>?<TO|IN>}
        {<RB|VB.?|MD>*<TV><IN>?}
        {<TVP><CC><V.*>} 
    VB: {<RB><V.*>}         #Verb used to chunk the ANDTARGET chunk
    ANDT: {<CC><TVP><NP.?>} #and action B
    ANDTARGET: {<NP><V.*><.*>*<ANDT>} #A verb sth and action B
            {<NP><ANDT><ANDT>}
            {<NP><ANDT>}
            {<NP><TVP><.*>*<ANDT>}
    THATT: {<WHICH><TVP><NP.?>} #that/which action B
    THATTARGET: {<NP><CC>?<THATT>} #a that/which action B
                {<NP><V.*><THATT>}
"""

def accuracy(correct, myanswer):
    TP = 0
    FP = 0
    FN = 0
    c = False
    for answer in myanswer:
        for canswer in correct:
            if str(answer) in canswer:
                TP += 1
                c = True
        if not c:
            FP += 1

    FN = len(correct) - TP
    precision = TP/ (TP+FP)
    recall = TP / (TP+FN)
    fscore = 2*(precision*recall)/(precision+recall)

    #print(TP)
    #print(FP)
    #print(FN)
    print('precision: ' + str(precision))
    print('recall: '+ str(recall))
    print('F-score:' + str(fscore))
    

if __name__ == '__main__':
    tresultList = []
    vresultList = []
    tcorrectList = []
    vcorrectList = []
    sentences = load()
    ## training / validation sets
    training = []
    validation = []
    for i, sent in enumerate(sentences):
        if i%10 == (3 or 8):
            validation.append(sent)
            vcorrectList.append(correctset[i])
        else: 
            training.append(sent)
            tcorrectList.append(correctset[i])

    training_tagged_sents = preprocess(training)
    validation_tagged_sents = preprocess(validation)
    cp = nltk.RegexpParser(grammar, loop=10)
    for tsent in training_tagged_sents:
        tresultList.append(checktree(tsent))
    for vsent in validation_tagged_sents:
        vresultList.append(checktree(vsent))

    accuracy(tcorrectList, tresultList)
    accuracy(vcorrectList, vresultList)
    print(tresultList)
    print(vresultList)

