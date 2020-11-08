import hashlib
import os
import pickle
import re
import time

import numpy as np
import requests


def md5_hash(arr):
    if type(arr) == np.ndarray:
        arr = arr.tolist()
    return(hashlib.md5(pickle.dumps([[str(i).encode('utf-8') for i in j] for j in arr])).hexdigest())

def get_last10_md5():
    cols = ["date_operation","date_valeur","type","description","debit","credit"]

    req = requests.get("http://192.168.1.100:8001/operation/scraped/last10")
    
    if req.status_code != 200:
        raise requests.exceptions.HTTPError

    last10 = req.json()
    last10 = [[i[c] for c in cols] for i in last10]
    last10 = np.asarray(last10)

    return md5_hash(last10) 
    
def push_notification(text, config):
    requests.post("https://api.pushed.co/1/push", data={
        "app_key" : os.getenv('PUSHED_APP_KEY'),
        "app_secret" : os.getenv('PUSHED_APP_SECRET'),
        "target_type" : "app",
        "content" : text,
    })

def parse_date(date):

    date = time.strptime(date, '%b %d, %Y %I:%M:%S %p')
    date = time.strftime('%Y-%m-%d', date)
    return date

def parse_montant(montant):
    if montant[0] == '-':
        debit = re.sub(',','.',re.sub('[-+] ?([0-9, ]*).*','\\1',montant)).strip()
        debit = str(float(re.sub(' ','',debit)))
        credit = str(float(0))
    else:
        credit = re.sub(',','.',re.sub('[-+] ?([0-9, ]*).*','\\1',montant)).strip()
        credit = str(float(re.sub(' ','',credit)))
        debit = str(float(0))

    return debit, credit

def load_more(driver):
    if driver.browser.find_element_by_css_selector('.js-Operations-more').is_displayed():
        driver.browser.execute_script("$('.js-Operations-more').click()")
        time.sleep(.5)

        while True:
            try:
                driver.browser.find_element_by_css_selector('.Operations-more--loading')
                time.sleep(0.5)
            except:
                break
        return True
    else:
        return False
