import nltk
import random
from nltk.corpus import wordnet as wn
from nltk.corpus import gutenberg
from nltk.corpus import brown
from nltk.corpus import stopwords
from nltk.collocations import *
from nltk.probability import ConditionalFreqDist

#########################################################################
"Overview of approach"
"""
1. input corpora
I used for input corpus, brown, treebank, chat, and conll2000, which are tagged corpus.
2. Extracting possible pairs
in the tagged input corpora, find 'adv'+'adj' and 'adv' + 'n' (endswith -ness) pairs.
Discard pairs which w2 in (w1,w2) used more than twice.
Make conditional frequency distribution (dictionary) for (w1,w2)
3. Ranking
for each (w1,w2), evaluate conditonalfreqdist[w1][w2]/freqdist[w1], use this measure as uniqueness.
Sort them in descending order.
"""
#########################################################################

########## input text corpora ##########
# used four input corpora, brown, treebank,nps_chat, and conll2000 (all tagged)
# importcorpora() for getting tagged sents - for word pair extraction
def importcorpora():
    b = brown.tagged_sents(tagset='universal')
    t = nltk.corpus.treebank.tagged_sents(tagset='universal')
    c = [nltk.corpus.nps_chat.tagged_words(tagset='universal')]
    c2 = nltk.corpus.conll2000.tagged_sents(tagset='universal')
    return b+t+c+c2

#importcorpora2() for getting unttaged words - for finding word frequency
def importcorpora2():
    b = brown.words()
    t = nltk.corpus.treebank.words()
    c = nltk.corpus.nps_chat.words()
    c2 = nltk.corpus.conll2000.words()
    return b+t+c+c2
    
########## extracting possible word pairs ##########
# use POS tag in tagged corpora. 
# extract 'adv'-'adj' pairs. If certain adj is used more than once, those paired adverbs are regarded as non-intensifiers
# (discarded for accuracy)
def advadj(corpora):
    pairs = []
    for tagged_sent in corpora:
        for (w1, t1), (w2, t2) in nltk.bigrams(tagged_sent):
           if (t1=='ADV' and t2=='ADJ' and w1 not in stopwords.words('english')): #extract word pairs : 'adv' + 'adj', discard stopwords
                pairs.append((w1.lower(), w2.lower())) 
    cfdist = ConditionalFreqDist((w2, w1) for (w1,w2) in pairs) #construct cfd for wordpairs
    newcfdist = ConditionalFreqDist()
    for w1 in cfdist:
        if len(cfdist[w1])==1: #use only when certain adj is used only once
            w2 = list(cfdist[w1])[0]
            newcfdist[w2][w1] = cfdist[w1][w2] 
    return newcfdist #return cfd with (w1, w2)

# extract 'adj' - 'n' pairs. only used nouns ends with '-ness' (an example of abstract noun)
# discard with same criteria as above (for accuracy)
def adjn(corpora):
    pairs = []
    for tagged_sent in corpora:
        for (w1, t1), (w2, t2) in nltk.bigrams(tagged_sent):
            if (t1=='ADJ' and t2=='NOUN' and w2.endswith('ness') and w1 not in stopwords.words('english')): #extract word pairs
                pairs.append((w1.lower(), w2.lower())) 

    cfdist = ConditionalFreqDist((w2, w1) for (w1,w2) in pairs)
    newcfdist = ConditionalFreqDist()
    for w1 in cfdist:
        if len(cfdist[w1])==1:
            w2 = list(cfdist[w1])[0]
            newcfdist[w2][w1] = cfdist[w1][w2]
    return newcfdist #return cfd with (w1,w2)

########## Ranking ##########
# for each (w1,w2), uniqueness = conditonalfreqdist[w1][w2]/freqdist[w1]
# freq constructs the fd for intensifiers
def freq(corpus):  
    fdist = nltk.FreqDist(w.lower() for w in corpus)
    return fdist

# evaluate uniquness, shuffle the list, and sort them by uniqueness (descending order)
def ranking(cfdist, fdist):
    final = []
    for w1 in cfdist:
        if fdist[w1]>50: continue      #cutoff: if the intensifiers are used more than 50 times, it is not likely to be an intensifier (e.g. 'soon')
        if len(cfdist[w1])>3: continue #cutoff: if the intensifiers are decorating more than 3 lexicons, it is more likely to be a general intensifier (e.g. 'greatly')
        for w2 in cfdist[w1]:
            cfd = cfdist[w1][w2]
            fd = fdist[w1]
            uniqueness = cfd/fd
            final.append((w1, w2, uniqueness,cfd)) #calculate uniqueness
    random.shuffle(final)   #shuffle
    return sorted(final, key = lambda triple : (-triple[2], -triple[3])) #sort in descending order with uniqueness

if __name__ == '__main__':
    cfd1 = advadj(importcorpora())   #conditional frequency distribution from adv-adj pairs
    cfd2 = adjn(importcorpora())     #conditional frequency distribution from adj-n (-ness) pairs
    cfd = dict(cfd2, **cfd1)         #combining two cfds above
    fd = freq(importcorpora2())                      #finding the frequency distribution of intensifiers in cfd
    l = ranking(cfd, fd)             #sort with uniqueness

    #f = open("CS372_HW2_output_20180526.csv", "w")
    f = open("test2.csv", "w")
    for (w1, w2, u, cfd) in l[:100]:
        f.write(w1 + ',' + w2 + '\n')

