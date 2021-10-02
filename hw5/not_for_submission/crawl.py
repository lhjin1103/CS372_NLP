from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import json

def crawl(url):
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser") 
    body = soup.select('#bodyContent')
    return(body[0].text)

crawl('https://en.wikipedia.org/wiki/Norberto_Alonso')

if __name__ == '__main__':
    
    dev_file = open("gap-development.tsv", 'r', encoding='utf-8')
    dev_read_file = csv.reader(dev_file, delimiter="\t")
    dev_set = []
    for line in dev_read_file:
        dev_set.append(line)
    dev_set = dev_set[1:]
    
    test_file = open("gap-test.tsv", 'r', encoding='utf-8')
    test_read_file = csv.reader(test_file, delimiter="\t")
    test_set = []
    for line in test_read_file:
        test_set.append(line)
    test_set = test_set[1:]
    
    dev_url = {}
    for line in dev_set:
        tid = line[0]
        url = line[10]
        try:
            dev_url[tid] = crawl(url)
        except: 
            print (tid, url)
    
    test_url = {}
    for line in test_set:
        tid = line[0]
        url = line[10]
        try:
            test_url[tid] = crawl(url)
        except: 
            print (tid, url)


    with open('dev_url.json', 'w') as dev_file:
        json.dump(dev_url, dev_file, ensure_ascii=False)

    with open('test_url.json', 'w') as test_file:
        json.dump(test_url, test_file, ensure_ascii=False)