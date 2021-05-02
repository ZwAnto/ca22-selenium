import re
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from scraper import (get_last10_md5, load_more, md5_hash, parse_date,
                     parse_montant)

from scraper.logging import logging

logger = logging.getLogger(__name__)


class Browser:
    
    def __init__(self,chromedriver_path):
        
        # Drivers options
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--incognito")
        self.option.add_argument("--headless")
        self.option.add_argument("--no-sandbox")
        self.option.add_argument("--disable-gpu")
        self.option.add_argument("--log-level=3") 
        self.option.add_argument("--disable-dev-shm-usage")

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


    def retrieve(self,account):

        last_md5 = get_last10_md5()

        self.browser.get('https://www.credit-agricole.fr/ca-cotesdarmor/particulier/operations/synthese/detail-comptes.html?idx={}&famillecode=1#!/'.format(account))

        out = []
        history_reached = False

        start = 0
        while not history_reached:

            ops = self.browser.find_elements_by_css_selector('#bloc-operations li')

            ith = start
            for ith in range(start, len(ops)):    
                logger.info(f'Parsing operation {ith+1}.')

                op = ops[ith]

                date_op = parse_date(op.find_element_by_css_selector("#dateOperation").get_attribute('aria-label'))
                date_val = parse_date(op.find_element_by_css_selector("#dateValeur").get_attribute('aria-label'))
                
                op_type = op.find_element_by_css_selector("div.Operation-type").get_attribute('textContent').strip()
                op_name = op.find_element_by_css_selector("div.Operation-name").get_attribute('textContent').strip()
                debit, credit = parse_montant(op.find_element_by_css_selector("#montant").get_attribute('aria-label'))

                for i in op.find_elements_by_css_selector('.Operation-list .Operation-main div'):
                    op_name = op_name + ' ' + i.get_attribute("textContent")

                op_name = re.sub('\n',' ',op_name)
                op_name = re.sub('\t',' ', op_name)
                op_name = re.sub('[ ]{1,}',' ', op_name)
                op_name = op_name.strip()

                logger.info([date_op, date_val, op_type, op_name, debit, credit])

                out.append([date_op, date_val, op_type, op_name, debit, credit])

                if last_md5 is not None:
                    md5 = md5_hash(out[-10:]) 
                    if md5 == last_md5:
                        out = out[:-10]
                        history_reached = True
                        break
                    
            start = ith+1

            if not load_more(self):
                break

        out = [{
            "date_operation": i[0],
            "date_valeur": i[1],
            "type": i[2],
            "description": i[3],
            "debit": float(i[4]),
            "credit": float(i[5])
            } for i in out]

        return(out)