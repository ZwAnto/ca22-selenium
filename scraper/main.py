
import json
import logging
import os

import plac
import pyaml
import requests
from selenium.common.exceptions import WebDriverException

from scraper import push_notification
from scraper.browser import Browser

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s',level=logging.INFO)

def main(config_file='config.yml'):

    try:
        config = pyaml.yaml.load(open(config_file), Loader=pyaml.yaml.loader.BaseLoader)

        chrome = Browser(config['chromedriver'])
        chrome.connect(**config['login'])

        operations = chrome.retrieve(config['bank_account'])

        chrome.quit()

        if len(operations) == 0:
            push_notification('Database up-to-date.', config)
        else:
            operations = list(reversed(operations))

            for operation in operations:
                print(operation['description'])
                r = requests.post('http://192.168.1.100:8001/operation/scraped/', data = json.dumps(operation), headers={"Content-Type": "application/json"})
                
                if r.status_code != 200:
                    raise requests.exceptions.HTTPError
            
            push_notification('%i new operations added.' % (len(operations)), config)

    except FileNotFoundError as e:
        logging.error('Configuration file not found.')
        push_notification('Configuration file not found.', config)

    except pyaml.yaml.scanner.ScannerError as e:
        logging.error('Error during config file parsing.')
        push_notification('Error during config file parsing.', config)

    except WebDriverException as e:
        logging.error('Error with slenium driver.')
        push_notification('Error with slenium driver.', config)

    except requests.exceptions.HTTPError as e:
        logging.error('Error during communication with fastapi.')
        push_notification('Error during communication with fastapi.', config)

    except Exception as e:
        logging.error('Unknown Exception occured.')
        push_notification('Unknown Exception occured.', config)
        raise e

    finally:
        exit()

if __name__ == '__main__':
    import plac; plac.call(main)
