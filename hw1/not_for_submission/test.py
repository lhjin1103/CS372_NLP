from nltk.corpus import wordnet as wn
from nltk.corpus import gutenberg
import nltk
from nltk.corpus import stopwords
from nltk.book import *
from nltk.collocations import *

tokens_all=gutenberg.words()
gut_text = nltk.Text(tokens_all)

boosters = ['absolutely', 'amazingly', 'completely', 'deeply', 'enormously', 'entirely', 'extremely', 'fabulously', 'fricking', 'fully', 'greatly', 'highly', 'hugely', 'incredibly', 'intensly', 'purely', 'really', 'remarkably', 'substantially', 'thoroughly', 'totally', 'tremendously', 'unbelievably', 'very', 'exceedingly', 'certainly', 'definitely', 'clearly', 'strongly']

unrecog = ['I', 'my', 'me', 'mine', 'you', 'your', 'yours', 'he', 'his', 'him', 'she', 'her', 'hers', 'it', 'its', 'they', 'their', 'them', 'the', 'that', 'those', 'but', 'is', 'are', 'soon', 'and', 'not', 'a', 'an', 'of', 'for','be', 'been', 'were', 'was', 'become', 'became', 'do', 'did']

#more, most, flipping, ...  deleted from the boosters list.
#exceedingly, certainly, definitely, clearly added to the list

def adjset(text):
	adjlist = [w for w in text if wn.synsets(w, 'a') or wn.synsets(w, 's')]
	return set(adjlist)

def verbset(text):
	verblist = [w for w in text if wn.synsets(w, 'v')]
	return set(verblist)

def findBigrams(text, unrecognized, booster):
	bigram_measures = nltk.collocations.BigramAssocMeasures()
	finder = BigramCollocationFinder.from_words(text)
	#filters words that are not not alphabets, which are in unrecognized word list, bigrams not containing booster words
	#Also filters the words with nouns or words not in the dict.
	finder.apply_word_filter(lambda w: not w[0].isalpha())
	finder.apply_word_filter(lambda w: w in unrecognized)
	finder.apply_ngram_filter(lambda w1, w2: (w1 not in booster and w2 not in booster))
	finder.apply_word_filter(lambda w: wn.synsets(w)==[]) 
		#or  wn.synsets(w)[0].pos() =='n')
	finder.apply_freq_filter(2)
	return finder.nbest(bigram_measures.likelihood_ratio, 500)

def syndict(wordlist):
	returndict = {}
	for w in wordlist:
		if w[-2:] == ('ed'): continue
		if w in boosters: continue
		syn = []
		for synset in wn.synsets(w, pos='v'):
			syn += synset.lemma_names()
		l = list(set(syn))
		if w.lower() in l: l.remove(w.lower())
		for s in l:
			if wn.synsets(s)[0].pos()!= ('v'):
					l.remove(s)
		if 0<len(l)<16: returndict[w] = l
	return returndict


	
def wordpair(text, synset, bgramset):
	lst = []
	for (w1, w2) in bgramset:
		if w2 in synset:
			for s2 in synset[w2]:
				if s2 in text:
					lst.append((w1,w2,s2))
		elif w1 in synset:
			for s1 in synset[w1]:
				if s1 in text:
					lst.append((w1,w2,s1))

	for (w1, w2, s) in lst:
		for (a, b) in bgramset:
			if s==(a or b):
				lst.remove((w1,w2,s))
				break
	
	return lst

if __name__ == '__main__':
	adj= verbset(gut_text)
	syn = syndict(adj)
	bgram = findBigrams(gut_text, unrecog, boosters)
	l = wordpair(gut_text, syn, bgram)
	print(l)
