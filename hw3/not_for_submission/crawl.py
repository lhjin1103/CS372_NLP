import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import json
from nltk.tag import pos_tag
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

#if __name__ == '__main__':
def crawl():
    js = {}    
    for i in range(1, 50):
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
    for play in js:
        d[play] = []
        for block in js[play]:
            l = ' '.join(block)
            l = l.replace('\n', ' ')
            l = l.replace('\xa0', ' ')
            l = l.replace('*', ' ')
            l = re.sub('\d*\d\)', '', l)
            m = sent_tokenize(l)
            if "" in m:
                m.remove("")
            if m!= []:
                d[play].append(m)

    wd = {}
    for play in d:
        wd[play] = []
        for sent in d[play]:
            for s in sent:
                w = word_tokenize(s)
                if len(w)>3:
                    wd[play].append(w)
    
    pos = {}
    for play in wd:
        pos[play] = []
        for sent in wd[play]:
            p = pos_tag(sent)
            pos[play].append(p)

    with open('text.json', 'w') as json_file:
        json.dump(wd, json_file, ensure_ascii=False)

    with open('tagged_text.json', 'w') as pos_file:
        json.dump(pos, pos_file, ensure_ascii=False)
     
    return wd
