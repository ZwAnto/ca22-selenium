from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import re
import sys

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
  
    def connect(self,account,passwd):
        self.browser.get("https://www.ca-cotesdarmor.fr/")
        self.browser.find_element_by_css_selector('#acces_aux_comptes a').click()
        self.browser.find_element_by_css_selector('input[name="CCPTE"]').send_keys(account)

        map = np.zeros((10,2),dtype='uint8')

        for i in range(25):
            j = str(i // 5 + 1)
            k = str(i % 5 + 1)
            
            css = '#pave-saisie-code tr:nth-of-type(' + j + ') td:nth-of-type(' + k + ')'
            a = self.browser.find_element_by_css_selector(css)
            
            if a.text.strip() != '':
                map[int(a.text.strip())] = (j,k)

        for i in passwd:
            css = '#pave-saisie-code tr:nth-of-type(' + str(map[int(i),0]) + ') td:nth-of-type(' + str(map[int(i),1]) + ')'
            self.browser.find_element_by_css_selector(css).click()
        
        self.browser.find_element_by_css_selector('span.droite a:nth-of-type(2)').click()
        self.browser.find_element_by_css_selector('#btn-sos_2').click()

    def retrieve(self,account,last=None):
        try:
            self.browser.find_element_by_css_selector('#bnc-compte-href').click()
            self.browser.find_element_by_xpath("//a[contains(., '" + account + "')]").click()
            
            date_pattern = re.compile('[0-9]{2}/[0-9]{2}')

            out=[]
            first = True
            page = 1
            match = 0

            while True:
                try:
                    if first:
                        first = False
                    else:
                        # Hiding sidebar 
                        self.browser.execute_script("$('#oic-container').hide()")
                        # Click for next page
                        self.browser.find_element_by_css_selector('a#lien_page_suivante').click()

                    rows = self.browser.find_elements_by_css_selector('.ca-table:nth-of-type(2) tbody tr')
                    
                    self.browser.find_element_by_css_selector('#PLIER_DEPLIER_OPERATIONS_O').click()
                    
                    for row in rows:
                        cols = row.find_elements_by_css_selector("td")
                        row_out = []
                        for idx, col in enumerate(cols):
                            if idx == 3:
                                split = col.text.split('\n')

                                text = ' '.join(split[1:])

                                date = date_pattern.findall(text)
                                if len(date):
                                    row_out.append(date[0])
                                    text = date_pattern.sub('',text)
                                else:
                                    row_out.append('')

                                row_out.append(split[0])
                                row_out.append(text)
                            elif idx not in [2,4]:
                                row_out.append(col.text)

                        if len(row_out):
                            out.append(row_out)
                            if last is not None:
                                if row_out == last[match]:
                                    match += 1
                                else:
                                    match = 0
                        if last is not None:
                            if match == (len(last)-1):
                                break
                    if last is not None:
                        if match == (len(last)-1):
                            print('Operations already up to date.')
                            break
                    sys.stdout.write('\rpage: ' + str(page) + ' obs: ' + str(len(out)))
                    sys.stdout.flush()
                    page += 1 
                except NoSuchElementException:
                    break
            if last is not None:
                if match:
                    out = out[:-match]
            return(out)
        except Exception as e: 
            print(str(e))
            self.quit()

    def quit(self):
        self.browser.quit()