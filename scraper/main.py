
import json
from scraper.logging import logging

import os

import plac
import requests
from selenium.common.exceptions import WebDriverException

from scraper import push_notification
from scraper.browser import Browser
  
logger = logging.getLogger(__name__)

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
            logger.info('Database up-to-date.')
            push_notification('Database up-to-date.')
        elif len(operations) > 50:
            logger.error('Too many operations to add. Please check for errors.')
            push_notification('Too many operations to add. Please check for errors.')
            exit(1)
        else:
            operations = list(reversed(operations))

            for operation in operations:
                print(operation['description'])
                r = requests.post('http://192.168.1.100:8001/operation/scraped/', data = json.dumps(operation), headers={"Content-Type": "application/json"})
                
                if r.status_code != 200:
                    raise requests.exceptions.HTTPError
            
            logger.info('%i new operations added.' % (len(operations)))
            push_notification('%i new operations added.' % (len(operations)))

    except WebDriverException as e:
        logger.error('Error with slenium driver.')
        push_notification('Error with slenium driver.')

    except requests.exceptions.HTTPError as e:
        logger.error('Error during communication with fastapi.')
        push_notification('Error during communication with fastapi.')

    except Exception as e:
        print(e)
        logger.error('Unknown Exception occured.')
        push_notification('Unknown Exception occured.')
        raise e

    finally:
        exit()

if __name__ == '__main__':
    import plac; plac.call(main)
