from flask import Flask, request, jsonify, abort
import requests
from bs4 import BeautifulSoup
from anticaptchaofficial.recaptchav2proxyless import *


app = Flask(__name__)


app.config.from_object("config.Config")

cookies = None

def login():
    global cookies
    session = requests.session()
    url = 'https://www.freepik.com/profile/login'
    SITE_KEY='6LfEmSMUAAAAAEDmOgt1G7o7c53duZH2xL_TXckC'
    KEY = '352a2c20725eda726a24c0788bbc71ac'
    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(app.config['KEY'])
    solver.set_website_url(url)
    solver.set_website_key(app.config['SITE_KEY'])

    g_response = solver.solve_and_return_solution()
    
    username = app.config['USERNAME']
    password = app.config['PASSWORD']

    urlLogin = 'https://www.freepik.com/profile/request/login'
    if g_response != 0:
        login_data =  {'login_email':username, 
                        'password':password,
                        'token_recaptcha':g_response,
                        'kfc': 1597044371177,'o':"aHR0cHM6Ly8=",
                        'remember':True,
                        'ref_landing': "",'register_callback': ""}
        s = session.post(url, data=login_data)
        cookies = s.cookies
        
    else:
        print("task finished with error "+solver.error_code)
        cookies = None
trust_ip = app.config['TRUST_IP']

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trust_ip:
        abort(403)  # Forbidden

@app.route('/', methods = ['POST'])
def getLink():
    if cookies:
        url = request.args['url']
        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}    

        try:    
            res = requests.get(url,headers=header,cookies=cookies)
            soup = BeautifulSoup(res.text,'lxml')
            link = soup.find('a',class_='download-button')['href']
            return jsonify(link)
        except Exception as err:
            login()
            print(f'ERROR: {err}') 
        return 'ERROR TRY AGAIN'

if __name__ == '__main__':
    login()
    app.run()