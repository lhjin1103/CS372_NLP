import json
import requests
import nltk

pd = nltk.corpus.cmudict.dict()

def heteronymlist():
    newlist = []
    for key in pd:
        if len(pd[key]) != 1:
            newlist.append(key)
    return newlist

heteronym = heteronymlist()

def main():
    with open("dictfile.json", "w") as json_file:
        for word in heteronym:
            url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word.lower()
            r = requests.get(url)
            if r.status_code==200:
                json.dump(r.json(), json_file)

if __name__ == '__main__':
    wordlist = heteronym
    d = {}
    for word in wordlist:
        print(word)
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + word.lower()
        r = requests.get(url)
        if r.status_code==200:  
            js = r.json()
            if len(js) != 1 :
                for pron in js:
                    for POS in pron['meanings']:
                        if not 'phonetic' in pron:
                            phon = 'unknown'
                        else:
                            phon = pron['phonetic']
                        if 'noun' in POS['partOfSpeech']:
                            if 'synonyms' in POS['definitions'][0]:
                                try:
                                    d[word]["N"][phon] = POS['definitions'][0]['synonyms']
                                except:
                                    try:
                                        d[word]["N"] = {phon: POS['definitions'][0]['synonyms']}
                                    except:
                                        d[word] = {"N":{phon: POS['definitions'][0]['synonyms']}}
                            else:
                                try:
                                    d[word]["N"][phon] = []
                                except:
                                    try:
                                        d[word]["N"] = {phon: []}
                                    except:
                                        d[word] = {"N":{phon: []}}
                        elif 'verb' in POS['partOfSpeech']:
                            if 'synonyms' in POS['definitions'][0]:
                                try:
                                    d[word]["V"][phon] = POS['definitions'][0]['synonyms']
                                except:
                                    try:
                                        d[word]["V"] = {phon: POS['definitions'][0]['synonyms']}
                                    except:
                                        d[word] = {"V":{phon: POS['definitions'][0]['synonyms']}}
                            else:
                                try:
                                    d[word]["V"][phon] = []
                                except:
                                    try:
                                        d[word]["V"] = {phon: []}
                                    except:
                                        d[word] = {"V":{phon: []}}
                        elif 'adj' in POS['partOfSpeech']:
                            if 'synonyms' in POS['definitions'][0]:
                                try:
                                    d[word]["ADJ"][phon] = POS['definitions'][0]['synonyms']
                                except:
                                    try:
                                        d[word]["ADJ"] = {phon: POS['definitions'][0]['synonyms']}
                                    except:
                                        d[word] = {"ADJ":{phon: POS['definitions'][0]['synonyms']}}
                            else:
                                try:
                                    d[word]["ADJ"][phon] = []
                                except:
                                    try:
                                        d[word]["ADJ"] = {phon: []}
                                    except:
                                        d[word] = {"ADJ":{phon: []}}
                        elif 'adv' in POS['partOfSpeech']:
                            if 'synonyms' in POS['definitions'][0]:
                                try:
                                    d[word]["ADV"][phon] = POS['definitions'][0]['synonyms']
                                except:
                                    try:
                                        d[word]["ADV"] = {phon: POS['definitions'][0]['synonyms']}
                                    except:
                                        d[word] = {"ADV":{phon: POS['definitions'][0]['synonyms']}}
                            else:
                                try:
                                    d[word]["ADV"][phon] = []
                                except:
                                    try:
                                        d[word]["ADV"] = {phon: []}
                                    except:
                                        d[word] = {"ADV":{phon: []}}
                        
    with open('dictfile.json', 'w') as json_file:
        json.dump(d, json_file, ensure_ascii=False)
