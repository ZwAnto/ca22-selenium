
import numpy as np
from saveload import *
from scrapper import browser
import pandas as pd
import configparser

print('Reading config.ini ...')
config = configparser.ConfigParser()
config.read('config.ini')

https://stackoverflow.com/questions/46322165/dont-wait-for-a-page-to-load-using-selenium-in-python

print('Browser initialization ...')
chrome = browser(config['CHROME']['DRIVER'])
chrome.reset()
chrome.connect(config['LOGIN']['ACCOUNT'],
               config['LOGIN']['PASSWORD'])

print('Retrieving operation ...')
try:
    histo = load(config['SCRAPPER']['OUT'])
    new_histo = chrome.retrieve(config['BANK']['ACCOUNT'],histo[:10])

    if len(new_histo):
        print('Adding %i new entries.' % len(new_histo))
        histo = new_histo + histo
        save(histo,config['SCRAPPER']['OUT'])
except FileNotFoundError:
    histo = chrome.retrieve(config['BANK']['ACCOUNT'])
    save(histo,config['SCRAPPER']['OUT'])