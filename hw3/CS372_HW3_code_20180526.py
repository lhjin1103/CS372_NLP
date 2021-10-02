import nltk
import re
from nltk.tag import pos_tag
from nltk.corpus import gutenberg
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
import json
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.util import untag
from urllib.request import urlopen
from bs4 import BeautifulSoup

def crawl():
    """
    first, crawl blog posts and shakespeare play scripts in the internet.
    then, preprocess them.
    """

    js = {}    
    for i in range(1, 50): #50 pages are there!
        html = urlopen("https://equipsblog.wordpress.com/page/" + str(i))
        soup = BeautifulSoup(html, "html.parser") 
        article_list = soup.findAll('article')
        for article in article_list:
            try:
                title = article.select('header>h2')[0].text
                blocks = article.find('div', {'class':'entry-content'})
                text = blocks.text
                js[title] = [[text]]
            except:
                continue

    html = urlopen("http://shakespeare.mit.edu/")  
    soup = BeautifulSoup(html, "html.parser") 
    tag_list = (soup.select('html > body > p > table> tr:nth-child(2)>td>a'))
    htmllist = []
    for tag in tag_list:
        htmllist.append(tag.get('href'))    

    for html in htmllist:
        html2 = urlopen('http://shakespeare.mit.edu/' + html[:-10] + 'full.html')
        soup = BeautifulSoup(html2, "html.parser")
        title = soup.select('body > table > tr>td>tr>td>a:nth-child(2)')[0].text
        body = (soup.select('html > body'))
        blocks = body[0].findAll('blockquote')
        js[title] = []
        for block in blocks:
            l = [element for lis in block.select('blockquote>a') for element in lis]
            js[title].append(l)


    d = {}
    for play in js:                         #this step is for removing noise words
        d[play] = []
        for block in js[play]:
            l = ' '.join(block)             #join the spliced sentences into a block
            l = l.replace('\n', ' ')        #remove \n
            l = l.replace('\xa0', ' ')      #remove \xa0
            l = l.replace('*', ' ')         #remove *
            l = re.sub('\d*\d\)', '', l)    #remove 'number)'
            m = sent_tokenize(l)            #sentence tokenize
            if "" in m:
                m.remove("")
            if m!= []:
                d[play].append(m)

    wd = {}             
    for play in d:                          #this step is for word tokenizing
        wd[play] = []
        for sent in d[play]:
            for s in sent:
                w = word_tokenize(s)        #word tokenize
                if len(w)>3:                #only use sentences with more than three words -> for performance
                    wd[play].append(w)
    
    pos = {}
    for play in wd:
        pos[play] = []
        for sent in wd[play]:
            p = pos_tag(sent)               #pos tagging
            pos[play].append(p)

    #with open('text.json', 'w') as json_file:
    #    json.dump(wd, json_file, ensure_ascii=False)

    #with open('tagged_text.json', 'w') as pos_file:
    #    json.dump(pos, pos_file, ensure_ascii=False)
     
    return pos

cachedict = {}                                  #global cache dictionary for the synonym search
sword = stopwords.words('english')              #not going to count some short, frequent words such as 'a' or 'ay'
sword.append('ay')                              

def rank(sentdict):
    """
    for finding heteronyms, and count the numbers of heteronyms in each sentence.
    marking the heteronyms for further analysis
    """
    newlist = []
    for script in sentdict:
        for sent in sentdict[script]:
            hetlist = []
            counter = 0
            for i in range(len(sent)):
                word, pos = sent[i]
                if word.lower() not in sword and word.lower() in dict_data:
                    counter+=1
                    hetlist.append(i)

            if counter>1:
                if len(sent)>7:                                      #only used sentences longer than 7 words were used
                    newlist.append((sent, counter, hetlist, script)) #sentence, marked with the number of heteronyms, the indicies, and the citation
    return newlist

def final(countlist, sents):
    """
    using the sentences returned in 'rank',
    annotate the pronunciations in heteronyms and sort them in appropriate order
    """
    newlist = []
    for row in countlist:
        sent, counter, hetlist, citation = row
        hets = []
        for wordnum in hetlist:
            pron, pos = annotate(sent, wordnum, sents)                      #annotate the pronunciation
            if 'unknown' not in pron: 
                    hets.append((sent[wordnum][0], wordnum, pron, pos))     #only show the results with no 'unknown' marks.
        if counter == len(hets):
            numwords = len(set([het[0].lower() for het in hets]))           #number of different words
            numprons = len(set([het[2] for het in hets]))                   #number of different pronunciation
            numhomo = numprons - numwords                                   #number of homonym pairs
            numpos = len(set([het[3] for het in hets]))                     #number of POS
            if counter>2 and numwords==1: continue                          #if only one word in same pronunciation repeatedly appears, then think it as a noise sentence.
            newlist.append((sent, hets, counter, numhomo, numpos, numwords, citation)) 
 
    list.sort(newlist, key = lambda l : (-l[2], -l[3], l[4], -l[5]))
    return newlist
    
def annotate(sent, wordnum, sents):
    """
    called by function 'final'
    annotate the pronunciation in two cases, different POS, same POS.
    """
    (word, pos) = sent[wordnum]
    if pos.startswith('N'): p = 'N'         #give POS with same annotation in dictionary
    elif pos.startswith('V'): p = 'V'
    elif pos.startswith('R'): p = 'ADV'
    elif pos.startswith('J'): p = 'ADJ'
    else: p = pos
    try:
        if len(dict_data[word.lower()][p]) == 1:                        #only one possible pronunciation in given POS
            return (list(dict_data[word.lower()][p].keys())[0], p)      #then return that pronunciation
        else:                                                           #if there are multiple,
            return (findsyn(sent, wordnum, word.lower(), p, sents), p)  #then call findsyn and do context comparison
    except: 
        return ('pron of unknown pos', p)                               #if error: cannot find the word of that POS in the dictionary -> mark as unknown

def findsyn(sent, wordnum, word, pos, corpora, ws = 2, w1 = 8, w2=5, w3=2):
    """
    called by function 'annotate'
    do context comparison and return the appropriate pronunciation
    """
    synlist = {}
    for phon in dict_data[word][pos]:               #making a list of synonyms
        try:
            for syn in dict_data[word][pos][phon]:
                synlist[syn] = 0
        except: continue

    
    for syn in synlist:     
        if syn not in cachedict:
            cachedict[syn] = {}
            cachedict[syn]['before'] = []                                       #initialize of cachedict
            cachedict[syn]['after'] = []
            cachedict[syn]['before2'] = []
            cachedict[syn]['after2'] = []   
            cachedict[syn]['before3'] = []
            cachedict[syn]['after3'] = []           
            cachedict[syn]['sentence'] = []
            cachedict[syn]['counter'] = 0
            for s in corpora:
                for i in range(len(s)):
                    if s[i].lower()==syn:
                        cachedict[syn]['counter'] += 1
                        if i==0: cachedict[syn]['before'].append("")  
                        else: cachedict[syn]['before'].append(s[i-1])
                        if i<2: cachedict[syn]['before2'].append("")
                        else: cachedict[syn]['before2'].append(s[i-2])
                        if i<3: cachedict[syn]['before3'].append("")
                        else: cachedict[syn]['before3'].append(s[i-3])
                        if i==len(s)-1: cachedict[syn]['after'].append("")
                        else: cachedict[syn]['after'].append(s[i+1])
                        if i<len(s)-3: cachedict[syn]['after2'].append(s[i+2])
                        else: cachedict[syn]['after2'].append("")
                        if i<len(s)-4: cachedict[syn]['after3'].append(s[i+2])
                        else: cachedict[syn]['after3'].append("")
                        cachedict[syn]['sentence'] = cachedict[syn]['sentence'] + s
        similarity = 0                                                          #store the context information
        beforeword = "" if wordnum==0 else sent[wordnum-1][0]
        afterword = "" if wordnum==len(sent)-1 else sent[wordnum+1][0]
        beforeword2 = "" if wordnum<2 else sent[wordnum-2][0]
        afterword2 = "" if wordnum>len(sent)-3 else sent[wordnum+2][0]
        beforeword3 = "" if wordnum<3 else sent[wordnum-3][0]
        afterword3 = "" if wordnum>len(sent)-4 else sent[wordnum+3][0]

        for b in cachedict[syn]['before']:                                      #evaluate similarity
            if beforeword.lower() == b.lower(): similarity += w1
        for b2 in cachedict[syn]['before2']:
            if beforeword2.lower() == b2.lower(): similarity +=w2
        for b3 in cachedict[syn]['before3']:
            if beforeword3.lower() == b3.lower(): similarity +=w3
        for a in cachedict[syn]['after']:
            if afterword.lower() == a.lower() : similarity += w1
        for a2 in cachedict[syn]['after2']:
            if afterword2.lower() == a2.lower() : similarity += w2
        for a3 in cachedict[syn]['after3']:
            if afterword3.lower() == a3.lower(): similarity += w3
        for ss in cachedict[syn]['sentence']:
            for sw in sent:
                if sw[0].lower() == ss.lower(): similarity += ws
        if cachedict[syn]['counter']==0: similarity=0
        else: similarity = similarity/(10*cachedict[syn]['counter'])            #normalizing the count value to similarity
        synlist[syn] = similarity
    freq = []
    for phon in dict_data[word][pos]:                           
        if dict_data[word][pos][phon] == []:
            freq.append((phon, 1))
        else:
            syns = dict_data[word][pos][phon]
            f = max([synlist[syn] for syn in syns])                             #similarity of the pronunciation = maximum among the related synonyms
            freq.append((phon,f))
    list.sort(freq, key = lambda l : - l[1])                                    #annotate with the one with maximum similarity
    return freq[0][0]
            
if __name__ == '__main__':

    pos_data = crawl()                                #crawling + preprocessing

    with open('newdict.json') as json_file1:          #dictionary data stored in json file
        dict_data = json.load(json_file1) 
#    with open('tagged_text.json') as json_file2:     #this can be used with stored text file
#        pos_data = json.load(json_file2) 

    bsents = brown.sents()                            #standard corpus

    search = rank(pos_data)                           #search for heteronyms
    final = final(search, bsents)                     #annotate and sort
    f = open("CS372_HW3_output_20180526.csv", "w")
    for (sent, hets, counter, numhomo, numpos, numwords, citation) in final[:30]:       #top 30 outputs
        untagged = untag(sent)
        strsent = ' '.join(untagged)
        f.write('"' + strsent + '"' + ',' + '"' + str(hets) + '"' + ',' + '"' + citation + '"'+ '\n')

