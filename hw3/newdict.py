import json
import requests
import nltk
from nltk.corpus import wordnet as wn



pd = nltk.corpus.cmudict.dict()
d = {}
def stress(pron):
    return [i[-1] for i in pron if i[-1].isdigit()]

if __name__ == '__main__':

    for word in pd:
        prons = pd[word]
        if len(prons)==2:
            stresses = [stress(pron) for pron in prons]
            if stresses != [['0','1'], ['1','0']] and stresses!= [['1','0'], ['0','1']]: continue
            syndict = {'N': [], 'V': []}
            check = {'N': 0 , 'V' : 0}
            for synset in wn.synsets(word):
                if synset.name().startswith(word + '.'):
                    if synset.name()[-4] == 'n':
                        check['N'] += 1
                        for i in synset.lemmas():
                            if i.name() != word:
                                syndict['N'].append(i.name())
                    elif synset.name()[-4] == 'v':
                        check['V'] += 1
                        for i in synset.lemmas():
                            if i.name() != word:
                                syndict['V'].append(i.name())
            if check['N']==0 or check['V']==0 : 
                continue  
            if stresses == [['0','1'], ['1','0']]:
                d[word] = {}
                d[word]['V'] = {' '.join(prons[0]) : syndict['V']}
                d[word]['N'] = {' '.join(prons[1]): syndict['N']} 
            elif stresses == [['1','0'], ['0','1']]:
                d[word] = {}
                d[word]['V'] = {' '.join(prons[1]): syndict['V']}
                d[word]['N'] = {' '.join(prons[0]): syndict['N']} 

    with open('dictfile.json') as json_file:
        js = json.load(json_file)
    
    d.update(js)

    with open('newdict.json', 'w') as json_file:
        json.dump(d, json_file, ensure_ascii=False)


                    
