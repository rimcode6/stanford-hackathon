from flask import Flask, render_template
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import html2text
from boilerpy3 import extractors
from goose3 import Goose
#import urllib.parse; 
from os import environ 
import os

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
from urllib.parse import quote

app = Flask(__name__)


def parseSearch(query):
    def _create_frequency_table(text_string) -> dict:

        stopWords = set(stopwords.words("english"))
        words = word_tokenize(text_string)
        ps = PorterStemmer()

        freqTable = dict()
        for word in words:
            word = ps.stem(word)
            if word in stopWords:
                continue
            if word in freqTable:
                freqTable[word] += 1
            else:
                freqTable[word] = 1

        return freqTable


    def _score_sentences(sentences, freqTable) -> dict:
        sentenceValue = dict()

        for sentence in sentences:
            word_count_in_sentence = (len(word_tokenize(sentence)))
            for wordValue in freqTable:
                if wordValue in sentence.lower():
                    if sentence[:10] in sentenceValue:
                        sentenceValue[sentence[:10]] += freqTable[wordValue]
                    else:
                        sentenceValue[sentence[:10]] = freqTable[wordValue]

            sentenceValue[sentence[:10]] = sentenceValue[sentence[:10]] // word_count_in_sentence

        return sentenceValue

    def _find_average_score(sentenceValue) -> int:
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]

        # Average value of a sentence from original text
        average = int(sumValues / len(sentenceValue))

        return average


    def _generate_summary(sentences, sentenceValue, threshold):
        sentence_count = 0
        summary = ''

        for sentence in sentences:
            if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] > (threshold):
                summary += " " + sentence
                sentence_count += 1

        return summary
    #bodyJson = request.json
    #query = bodyJson["query"]
    safe_string = quote(query)
    searchUrl = "https://www.google.com/search?q=" + safe_string

    print("Search URL : ",searchUrl)
    page = requests.get(searchUrl)
    allGoogleSearchResults = []
    soup = BeautifulSoup(page.content)
    links = soup.findAll("a")
    for link in  soup.find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
        url = re.split(":(?=http)",link["href"].replace("/url?q=",""))[0]
        urlPostFixIndex = url.find('&sa=')
        if(urlPostFixIndex):
            url = url[0:urlPostFixIndex]
        allGoogleSearchResults.append(url)

    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    unProcessedHtmlStrings = []
    for html in allGoogleSearchResults:
        unProcessedHtmlStrings.append(str(requests.get(html,headers=headers).content))

    g = Goose()
    processedArticleStrings = []
    articleIndex = 1
    for html in unProcessedHtmlStrings:
        a = g.extract(raw_html=html)
        
        # 1 Create the word frequency table
        #freq_table = _create_frequency_table(a.cleaned_text)


        # 2 Tokenize the sentences
        #sentences = sent_tokenize(a.cleaned_text)

        #if(len(sentences) == 0):
        #    continue
        #print("Sentences : ",sentences)
        # 3 Important Algorithm: score the sentences
        #sentence_scores = _score_sentences(sentences, freq_table)

        # 4 Find the threshold
        #threshold = _find_average_score(sentence_scores)

        # 5 Important Algorithm: Generate the summary
        #summary = _generate_summary(sentences, sentence_scores, 1.5 * threshold)
        processedArticleStrings.append("Article {}.  {} : \n {}".format(articleIndex,a.title,a.cleaned_text))

        articleIndex += 1    
    return jsonify(articles=processedArticleStrings)

@app.route('/')
def hello():
    
    return render_template('dashboard.html')

@app.route('/upload',methods=['POST'])
def upload():

    name = request.form["name"]
    searchLinks = parseSearch(name)
    print(searchLinks)
    return searchLinks
    