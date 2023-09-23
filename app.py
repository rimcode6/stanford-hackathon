from flask import Flask, render_template
from flask import Flask, request, jsonify
#import requests
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


app = Flask(__name__)


def parseSearch(query):

        #bodyJson = request.json
        #query = bodyJson["query"]
        safe_string = urllib.parse.quote_plus(query)
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
            summary = _generate_summary(sentences, sentence_scores, 1.5 * threshold)
            processedArticleStrings.append("Article {}.  {} : \n {}".format(articleIndex,a.title,a.cleaned_text))

            articleIndex += 1    
        return jsonify(articles=processedArticleStrings)

@app.route('/')
def hello():
    
    return render_template('dashboard.html')

@app.route('/upload',methods=['POST'])
def upload():

    name = request.form["name"]
    print(name)
    return name
    