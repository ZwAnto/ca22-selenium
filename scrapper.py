from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import numpy as np
import re

class browser:
    
    def __init__(self,chromedriver_path):
        
        self.option = webdriver.ChromeOptions()
        self.option.add_argument(" — incognito")
        self.option.add_argument('--headless')
        self.option.add_argument('--no-sandbox')
        self.option.add_argument('--disable-gpu')
        self.option.add_argument('--disable-dev-shm-usage')

        self.chromedriver_path = chromedriver_path
        
        self.caps = DesiredCapabilities().CHROME
        self.caps["pageLoadStrategy"] = "none" 
        
        self.reset()
        
    def reset(self):
        self.browser = webdriver.Chrome(executable_path=self.chromedriver_path, options=self.option, desired_capabilities= self.caps)

    def waitForElement(self,selector,by=By.CSS_SELECTOR):
        el = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((by, selector)))
        return(el)
    
    def connect(self,account,passwd):
        WebDriverWait(self.browser.get("https://www.ca-cotesdarmor.fr/"), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#acces_aux_comptes a')))
        #a = self.browser.find_element_by_css_selector('#acces_aux_comptes a')
        a = self.waitForElement('#acces_aux_comptes a')
        a.click()

        #a = self.browser.find_element_by_css_selector('input[name="CCPTE"]')
        a = self.waitForElement('input[name="CCPTE"]')
        a.send_keys(account)
        

        map = np.zeros((10,2),dtype='uint8')

        for i in range(25):
            j = str(i // 5 + 1)
            k = str(i % 5 + 1)
            #a = self.browser.find_element_by_css_selector('#pave-saisie-code tr:nth-of-type(' + j + ') td:nth-of-type(' + k + ')')
            a = self.waitForElement('#pave-saisie-code tr:nth-of-type(' + j + ') td:nth-of-type(' + k + ')')
            if a.text.strip() != '':
                map[int(a.text.strip())] = (j,k)

        for i in passwd:
            #self.browser.find_element_by_css_selector('#pave-saisie-code tr:nth-of-type(' + str(map[int(i),0]) + ') td:nth-of-type(' + str(map[int(i),1]) + ')').click()
            a = self.waitForElement('#pave-saisie-code tr:nth-of-type(' + str(map[int(i),0]) + ') td:nth-of-type(' + str(map[int(i),1]) + ')').click()
        
        #self.browser.find_element_by_css_selector('span.droite a:nth-of-type(2)').click()
        a = self.waitForElement('span.droite a:nth-of-type(2)').click()
        #self.browser.find_element_by_css_selector('#btn-sos_2').click()
        a = self.waitForElement('#btn-sos_2').click()
             
    def retrieve(self,account,last=None):
        
        self.waitForElement('#bnc-compte-href').click()
        self.waitForElement("//a[contains(., '" + account + "')]",By.XPATH).click()
        
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
                    self.waitForElement('#oic-container')
                    self.browser.execute_script("$('#oic-container').hide()")
                    self.waitForElement('a#lien_page_suivante').click()

                a = self.waitForElement('.ca-table:nth-of-type(2)')
                rows = a.find_elements_by_css_selector("tr")
                self.waitForElement('#PLIER_DEPLIER_OPERATIONS_O').click()

                for row in rows:
                    cols = row.find_elements_by_css_selector("td")

                    row_out = []
                    for idx, col in enumerate(cols):
                        if idx == 3:
                            split = col.text.split('\n')
                            row_out.append(split[0])

                            text = ' '.join(split[1:])

                            date = date_pattern.findall(text)
                            if len(date):
                                row_out.append(date[0])
                                text = date_pattern.sub('',text)
                            else:
                                row_out.append('')
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

                print('page: %i obs: %i' % (page,len(out)))
                page += 1   
                if last is not None:
                    if match == (len(last)-1):
                            break     
            except:
                 break
        if last is not None:
            if match:
                out = out[:-match]
        return(out)