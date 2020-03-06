from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import re
import sys
import pickle
import hashlib
import time

def md5_hash(arr):
    if type(arr) == np.ndarray:
        arr = arr.tolist()
    return(hashlib.md5(pickle.dumps([[i.encode('utf-8') for i in j] for j in arr])).hexdigest())

class HistoryReachedError(Exception):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        errors = errors

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

  
    def connect(self,account,passwd):
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

        for i in passwd:
            map[i].click()
        
        self.browser.find_element_by_css_selector('#validation').click()

    def retrieve(self,account,last_md5=None):
        try:
            
            months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

            self.browser.execute_script("$('.npcd-mask').hide()")
            time.sleep(0.5)
            self.browser.find_element_by_css_selector('.SynthesisAccounts .SynthesisAccount:nth-of-type(1)').click()

            ops = self.browser.find_elements_by_css_selector('#bloc-operations li')

            def parse_date(date):
                date = re.split('[ ,]', date)
                month = [i+1 for i,m in enumerate(months) if m == date[0]][0]
                return date[1].zfill(2) + '/' + str(month).zfill(2)

            def parse_montant(montant):
                if montant[0] == '-':
                    debit = str(float(re.sub(',','.',re.sub('[-+] ?([0-9,]*).*','\\1',montant))))
                    credit = str(float(0))
                else:
                    credit = str(float(re.sub(',','.',re.sub('[-+] ?([0-9,]*).*','\\1',montant))))
                    debit = str(float(0))

                return debit, credit


            date_pattern = re.compile('[0-9]{2}/[0-9]{2}')

            out = []
            for op in ops:
                if len(out) == 10:
                    break
                try:
                    date_op = parse_date(op.find_element_by_css_selector("#dateOperation").get_attribute('aria-label'))
                    date_val = parse_date(op.find_element_by_css_selector("#dateValeur").get_attribute('aria-label'))
                    op_type = op.find_element_by_css_selector("div .Operation-type").text
                    op_name = op.find_element_by_css_selector("div .Operation-name").text
                    debit, credit = parse_montant(op.find_element_by_css_selector("#montant").text)

                    date_desc = date_pattern.findall(op_name)
                    date_desc = date_op if not len(date_desc) else date_desc[0]
                    
                    op_name = date_pattern.sub('', op_name)

                    for i in op.find_elements_by_css_selector('.Operation-main'):
                        op_name = op_name + ' ' + i.text

                    op_name = re.sub('\n','',op_name)

                    out.append([date_op, date_val, date_desc, op_type, op_name, debit, credit])

                    if last_md5 is not None:
                        md5 = md5_hash(out[-10:]) 
                        if md5 == last_md5:
                            raise(HistoryReachedError('a','a'))
    
                except NoSuchElementException:
                    break
                except HistoryReachedError:
                    new_md5 = md5_hash(out[:10])
                    out = out[:-10]
                    break
                else:
                    new_md5 = md5_hash(out[:10]) 
            return((out,new_md5))
        except Exception as e: 
            print(str(e))
            quit()

    def quit(self):
        self.browser.quit()