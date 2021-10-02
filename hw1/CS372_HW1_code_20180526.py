from nltk.corpus import wordnet as wn
from nltk.corpus import gutenberg
import nltk
from nltk.corpus import stopwords
from nltk.book import *
from nltk.collocations import *
import random

##########################brief introduction of the approach#########################
"""
1) intensity modifying words:
Intensity modifying words are originally from nltk.sentiment.vader -> booster_dict,
where the words have ‘incrementing’ effect. This list was further modified.
First, more and most, which are comparatives and superlatives, are deleted.
Also, ‘so’ is used a lot for the meaning ‘therefore’, thus removed.
Second, some intensity-modifying words such as exceedingly were added to the list
by finding adverbs appearing more than 50 times in the text, and then screened.
2) part-of-speech:
For the outputs, (adv+adj), (adv+v), (v+adv) are possible.
Here, I only used (adv+adj) since the othersdidn’t give significant amount of accurate outputs.
3) finding synonyms:
The main idea was using wordnet.synsets() method then was further modified by several criteria.
First, words end with ‘er’ and ‘st’ were regarded as comparative and superlative.
Then, only the words that are used as adj was used as synonyms.
Finally, words with too many synonyms was deleted in the dictionary for further accuracy.
(It tended to have not-very-similar words)
4) finding bigrams:
Bigrams were searched and filtered by BigramCollocationFinder.
Those bigrams have to contain an intensity-modifying word.
If they contain a word which does not have synsets (for example, names), or non-alphabets,
or unrecognized words (defined in unrecog, ex. he, I, did…), those bigrams are filtered.
From this step, I could get some possible word pairs that will be further used.
5) matching the synonyms: This is done by counting how many each synonyms are used alone and with intensity-modifying words.
For example, when we think about the synonyms, (good, excellent), good is often used with very,
but since very and excellent are both superlatives, excellent are not usually used with those intensity-modifying words.
Thus, if one synonym appears significantly with intensity-modifying words and one does not, then I picked those pairs."""
#####################################################################################


tokens_all=gutenberg.words()
gut_text = nltk.Text(tokens_all) #use all gutenberg texts for this homework

boosters = ['absolutely', 'amazingly','awfully', 'completely','considerably','decidedly', 'deeply','effing', 'enormously','especially','exceptionally', 'entirely', 'extremely', 'fabulously', 'flippin', 'flipping', 'fricking', 'frickin', 'frigging', 'friggin', 'fully', 'fucking', 'greatly','hella', 'highly', 'hugely', 'incredibly', 'intensly', 'majorly', 'purely', 'really', 'remarkably', 'substantially', 'thoroughly', 'totally', 'tremendously','uber',  'unbelievably','utterly', 'very', 'exceedingly', 'certainly','perfectly', 'seriously', 'wholly']
#intensity-modifying words originally from nltk.sentiment.vader -> boosters_dict, only choose 'incrementing' words.
#more, most deleted from the list: often used as comparative, superlative each
#so deleted from the list: often used to mean 'therefore'
#exceedingly, certainly, perfectly, seriously, wholly added to the list: by finding adverbs appearing more than 50 times in the text, and then screened

unrecog = ['I', 'my', 'me', 'mine', 'you', 'your', 'yours', 'he', 'his', 'him', 'she', 'her', 'hers', 'it', 'its', 'they', 'their', 'them', 'the', 'that', 'those', 'but', 'is', 'are', 'soon', 'and', 'not', 'a', 'an', 'of', 'for','be', 'been', 'were', 'was', 'become', 'became', 'do', 'did']

def adjset(text):
	adjlist = [w for w in text if wn.synsets(w, 'a') or wn.synsets(w, 's')]  #find possible adjectives in the text, and make the set of the list.
	return set(adjlist)

def verbset(text):
	verblist = [w for w in text if wn.synsets(w) and wn.synsets(w)[0].pos() == 'v'] #find possible verbs in the text, but not used to make the outputs.
	return set(verblist)

def findBigrams(text, unrecognized, booster):
	bigram_measures = nltk.collocations.BigramAssocMeasures()
	finder = BigramCollocationFinder.from_words(text)
	#filters words that are not not alphabets, which are in unrecognized word list, bigrams not containing booster words
	#Also filters the words with nouns or words not in the dict.
	finder.apply_word_filter(lambda w: not w[0].isalpha()) #non-alphabets
	finder.apply_word_filter(lambda w: w in unrecognized) #unrecognized words
	finder.apply_ngram_filter(lambda w1, w2: (w1 not in booster and w2 not in booster)) #no booster words
	finder.apply_word_filter(lambda w: wn.synsets(w)==[]) #not in the dict (no synsets)
	finder.apply_freq_filter(2) #collect if the bigram appears more than 2 times
	return finder.nbest(bigram_measures.likelihood_ratio, 500) #only filter the top 500 results. can be changed if desired.

def syndict(wordlist):  #making dictionary of synonyms. {word->[list of synonyms]}
	returndict = {}
	for w in wordlist:
		if w[-2:] == ('er' or 'st'): continue  #filter words ending with er or st. (words regarded as comparative and superlative each)
		if w in boosters: continue #filter booster words
		syn = []
		for synset in wn.synsets(w, pos='a' or 's'): #use if the words are used as adjective
			syn += synset.lemma_names()
		l = list(set(syn))
		if w.lower() in l: l.remove(w.lower()) #remove same word
		for s in l:
			if wn.synsets(s)[0].pos()!= ('a' or 's'): #remove if the synonym's usual meaning is not adjective (for better accuracy)
					l.remove(s)
		if 0<len(l)<16: returndict[w] = l #remove if there are too many synonyms (for better accuracy)
	return returndict


	
def wordpair(text, synset, bgramset):
#using the synonym dictionary, if an adjective in bigram has synonym and that synonym also appears in the text, check f that synonym appears with intensity-modifying words (using bigram set) in considerable frequency. If it doesn't appear with intensity-modifying words, regard it as desired word pair.
	lst = []
	for (w1, w2) in bgramset:
		if w2 in synset:
			for s2 in synset[w2]:
				if s2 in text:
					lst.append((w1,w2,s2)) #adj in bigram has synonym and it appears in the text
	for (w1, w2, s2) in lst:
		for (a, b) in bgramset:
			if s2==b:
				lst.remove((w1,w2,s2)) #that synonym does not appear with intensity-modifying words.
				break
	return lst

if __name__ == '__main__':
	adj= adjset(gut_text)
	syn = syndict(adj)
	bgram = findBigrams(gut_text, unrecog, boosters)
	l = wordpair(gut_text, syn, bgram)
	random.shuffle(l)   #choose 50 outputs randomly
	f = open("CS372_HW1_output_20180526.csv", "w")
	for (w1, w2, s) in l[:50]:
		f.write(w1 + ' ' + w2 + ',' + s + '\n')
	f.close()
