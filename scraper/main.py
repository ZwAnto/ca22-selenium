
import json
import logging
import os

import plac
import requests
from selenium.common.exceptions import WebDriverException

from scraper import push_notification
from scraper.browser import Browser

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s',level=logging.INFO)

def main():

    login = os.getenv('CA_LOGIN')
    password = os.getenv('CA_PASSWORD')
    account = os.getenv('CA_ACCOUNT')
    chromedriver = os.getenv('CHROMEDRIVER_PATH', 'chromedriver')

    try:

        chrome = Browser(chromedriver)
        chrome.connect(login, password)

        operations = chrome.retrieve(account)

        chrome.quit()

        if len(operations) == 0:
            logging.info('Database up-to-date.')
            push_notification('Database up-to-date.')
        else:
            operations = list(reversed(operations))

            for operation in operations:
                print(operation['description'])
                r = requests.post('http://192.168.1.100:8001/operation/scraped/', data = json.dumps(operation), headers={"Content-Type": "application/json"})
                
                if r.status_code != 200:
                    raise requests.exceptions.HTTPError
            
            logging.info('%i new operations added.' % (len(operations)))
            push_notification('%i new operations added.' % (len(operations)))

    except WebDriverException as e:
        logging.error('Error with slenium driver.')
        push_notification('Error with slenium driver.')

    except requests.exceptions.HTTPError as e:
        logging.error('Error during communication with fastapi.')
        push_notification('Error during communication with fastapi.')

    except Exception as e:
        logging.error('Unknown Exception occured.')
        push_notification('Unknown Exception occured.')
        raise e

    finally:
        exit()

if __name__ == '__main__':
    import plac; plac.call(main)
