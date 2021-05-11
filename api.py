import flask
from flask import request, jsonify
from bs4 import BeautifulSoup
import requests
import time
import json
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

@app.route('/api/v1/books/details', methods=['GET'])
def api_url():
    if 'url' in request.args:
        url = request.args['url']
        html = requests.get(url)

        # Check if an ID was provided as part of the URL.
        # If ID is provided, assign it to a variable.
        # If no ID is provided, display an error in the browser.
        soup = BeautifulSoup(html.content,'html.parser')
        rows = soup.find_all('div')

        # Create an empty dictionary for our results
        info = {}
        # Loop through the data and match results that fit the requested url.        
        for index in range(len(rows)):
            if index < 40:
                continue
            row = rows[index]
            str_rows = str(row)
            if "box-chap box-chap" in str_rows:
                cleantext = BeautifulSoup(str_rows, "lxml").get_text()    
                info['full_info'] = cleantext
                break

        title = soup.find_all('h2')
        cleanTitle = BeautifulSoup(str(title[0]), "lxml").get_text()
        info['title'] = cleanTitle
        return info
    else:
        return "Error: No url field provided. Please specify an url."

@app.route('/api/v1/books', methods=['GET'])
def api_books_url():
    if 'url' in request.args:
        info = {}
        url = request.args['url']
        html = requests.get(url)

        # Check if an ID was provided as part of the URL.
        # If ID is provided, assign it to a variable.
        # If no ID is provided, display an error in the browser.
        soup = BeautifulSoup(html.content,'html.parser')
        bookImg = soup.find_all('a',attrs ={"id":"bookImg"})
        info['img_url'] = bookImg[0].find('img')['src']

        bookInfo = soup.find_all('h1')
        info['book_info'] = bookInfo[0].get_text()

        bookId = soup.find_all('meta', attrs ={"name":"book_detail"})
        hiddenId = bookId[0]['content']
        info['chapter_name'] = []
        info['link'] = []
        info['season'] = []
        info['season_index'] = []
        firstSeason = soup.find_all('li', attrs ={"class":"divider-chap"})
        cleanFirstSeason = BeautifulSoup(str(firstSeason[0]), "lxml").get_text()
        info['season'].append(cleanFirstSeason)
        info['season_index'].append(0)

        start_time = time.time()        
        
        pagingUrl = "https://truyen.tangthuvien.vn/doc-truyen/page/" + hiddenId + "?page=0&limit=18446744073709551615&web=1"
        htmlTest = requests.get(pagingUrl)
        soupTest = BeautifulSoup(htmlTest.content,'html.parser')
        print("--- %s seconds ---" % (time.time() - start_time))

        rowTest = soupTest.find_all('ul')
        chapters = rowTest[0].find_all('li')

        for chap in chapters:
            try:
                info['chapter_name'].append(chap.find_all('a')[0]['title'])
                info['link'].append(chap.find_all('a')[0]['href'])
            except:
                season = chap.find_all('span')
                cleanSeason = BeautifulSoup(str(season[0]), "lxml").get_text()
                if info['season'][len(info['season']) - 1][:8] == cleanSeason[:8]:
                    continue
                info['season'].append(cleanSeason)
                info['season_index'].append(len(info['chapter_name']))

        
        # https://truyen.tangthuvien.vn/doc-truyen/page/31803?page=1&limit=75&web=1
        print("--- %s seconds ---" % (time.time() - start_time))
        app_json = json.dumps(info)
        return app_json
    else:
        return "Error: No url field provided. Please specify an url."
        
app.run()