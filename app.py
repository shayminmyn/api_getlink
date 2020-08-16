from flask import Flask, request, jsonify, abort , send_file
import requests
from bs4 import BeautifulSoup
import logging
import time
import os
import re
import zipfile
import io
import pathlib

app = Flask(__name__)

logFileName = 'logged_{}.txt'.format(time.strftime('%d-%B-%Y(%H-%M-%S)'))

logging.basicConfig(filename='logged/'+logFileName,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app.config.from_object("config.Config")
num_link_got = 0
trust_ip = app.config['TRUST_IP']
DOWNLOAD_PATH = app.config['DOWNLOAD_PATH']

file_name_requestted = []

def getFile(url):
    os.system('"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" ' + url)


def checkFileInQueue(file_name):
    if file_name in file_name_requestted:
        return False
    else:
        return True
def getFileName(url):
    regex = r'[^\/]+\_\d+\.htm$'
    item = re.findall(regex,url)[0]
    item = re.sub(r'\_\d+\.htm$','',item)
    return item

def checkFileExist(link):
    return os.path.isfile(link)

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trust_ip:
        abort(403)  # Forbidden



@app.route('/', methods = ['POST'])
def getLink():
    global num_link_got
    global file_name_requestted
    global DOWNLOAD_PATH
    url = request.json['url']
    file_name = getFileName(url)

    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}    

    try:    
        res = requests.get(url,headers=header)
        soup = BeautifulSoup(res.text,'lxml')
        link = soup.find('a',class_='download-button')['href']
        if checkFileInQueue(file_name):
            file_name_requestted.append(file_name)
            getFile(link)
        path = DOWNLOAD_PATH + file_name + '.zip'
        result = 'localhost:5000/download-zip?filename' + file_name
        timeout = time.time() + 60*3 #3 min
        while True:
            if time.time() > timeout:
                app.logger.error('Can\'t get file')
                abort(404)
            if checkFileExist(path):
                break
        file_stats = os.stat(path)
        size = file_stats.st_size
        num_link_got = num_link_got + 1
        app.logger.info('Number link got : {}'.format(num_link_got))
        file_name_requestted.remove(file_name)
        return jsonify(url=result,size=size)
    except Exception as err:
        num_link_got = 0
        # app.logger.info('Number link got : {} , Number link faild : {}'.format(num_link_got,num_link_faild))
        app.logger.error('Get link Error')
        abort(404)
    return 'ERROR TRY AGAIN'

@app.route('/download-zip')
def request_zip():
    global DOWNLOAD_PATH
    file_name = request.args.get('filename')
    base_path = pathlib.Path(DOWNLOAD_PATH + file_name + '.zip')
    data = io.BytesIO()

    with zipfile.ZipFile(data, mode='w') as z:
        z.write(base_path,file_name+'.zip')
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='download.zip'
    )

if __name__ == '__main__':
    app.run(host=app.config['MAIN_IP'])
