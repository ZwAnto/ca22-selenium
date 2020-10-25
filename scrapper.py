from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import re
import sys
import pickle
import hashlib
import time

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
DATE_PATTERN = re.compile('[0-9]{2}/[0-9]{2}')

def md5_hash(arr):
    if type(arr) == np.ndarray:
        arr = arr.tolist()
    return(hashlib.md5(pickle.dumps([[str(i).encode('utf-8') for i in j] for j in arr])).hexdigest())

def parse_date(date):
    date = re.split('[ ,]', date)
    month = [i+1 for i,m in enumerate(MONTHS) if m == date[0]][0]
    return date[1].zfill(2) + '/' + str(month).zfill(2), date[3] + '-' + str(month).zfill(2) + '-' + date[1].zfill(2) 

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

class browser:
    
    def __init__(self,chromedriver_path):
        
        # Drivers options
        self.option = webdriver.ChromeOptions()
        self.option.add_argument(" — incognito")
        self.option.add_argument('--headless')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-gpu')
        self.option.add_argument('--disable-dev-shm-usage')

        # Driver path
        self.chromedriver_path = chromedriver_path
        
        # Page load strategy
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = "normal" 
        # Initialize browser
        self.reset()
        
    def reset(self):
        self.browser = webdriver.Chrome(executable_path=self.chromedriver_path, options=self.option, desired_capabilities= self.caps)
        self.browser.set_window_size(1920, 1080)

    def quit(self):
        self.browser.quit()

    def connect(self,account,password):
        self.browser.get("https://www.credit-agricole.fr/ca-cotesdarmor/particulier/acceder-a-mes-comptes.html")
        time.sleep(0.5)
        self.browser.find_element_by_css_selector('input[name="CCPTE"]').send_keys(account)
        time.sleep(0.5)
        self.browser.find_element_by_css_selector('button[aria-label="Validation du code personnel"]').click()
        time.sleep(0.5)

        pass_btn = self.browser.find_elements_by_css_selector(".Login-keypad a")

        map = {}
        for i in pass_btn:
            map[i.find_element_by_css_selector('div').text] = i

        for i in password:
            map[i].click()
        
        self.browser.find_element_by_css_selector('#validation').click()
        time.sleep(5)

        pass

    def retrieve(self,account,last_md5=None):
        try:
            

            self.browser.get('https://www.credit-agricole.fr/ca-cotesdarmor/particulier/operations/synthese/detail-comptes.html?idx={}&famillecode=1#!/'.format(account))

            out = []
            history_reached = False

            while not history_reached:

                if not load_more(self):
                    new_md5 = md5_hash(out[:10]) 
                    break

                ops = self.browser.find_elements_by_css_selector('#bloc-operations li')

                for op in ops:

                    date_op, full_date = parse_date(op.find_element_by_css_selector("#dateOperation").get_attribute('aria-label'))
                    date_val, _ = parse_date(op.find_element_by_css_selector("#dateValeur").get_attribute('aria-label'))
                    op_type = op.find_element_by_css_selector("div .Operation-type").text
                    op_name = op.find_element_by_css_selector("div .Operation-name").text
                    debit, credit = parse_montant(op.find_element_by_css_selector("#montant").text)

                    date_desc = DATE_PATTERN.findall(op_name)
                    date_desc = date_op if not len(date_desc) else date_desc[0]
                    
                    op_name = DATE_PATTERN.sub('', op_name)

                    for i in op.find_elements_by_css_selector('.Operation-list .Operation-main div'):
                        op_name = op_name + ' ' + i.get_attribute("textContent")

                    op_name = re.sub('\n',' ',op_name)
                    op_name = re.sub('\t',' ', op_name)
                    op_name = re.sub('[ ]{1,}',' ', op_name)
                    op_name = op_name.strip()

                    out.append([date_op, date_val, date_desc, op_type, op_name, debit, credit, full_date])

                    if last_md5 is not None:
                        md5 = md5_hash(out[-10:]) 
                        if md5 == last_md5:
                            out = out[:-10]
                            new_md5 = md5_hash(out[:10])
                            history_reached = True
                            break

            return((out,new_md5))

        except Exception as e: 
            print(str(e))
            quit()


