import numpy as np
from saveload import *
from scrapper import browser
import pandas as pd
import configparser
import argparse
import sys 

parser = argparse.ArgumentParser()
parser.add_argument("conf", help="Configuration file") 
args = parser.parse_args()

sys.stdout.write('Reading config.ini... ')
sys.stdout.flush()
config = configparser.ConfigParser()
config.read(args.conf)
print('\033[92mOK\033[0m')

sys.stdout.write('Browser initialization... ')
sys.stdout.flush()
chrome = browser(config['CHROME']['DRIVER'])
print('\033[92mOK\033[0m')

sys.stdout.write('Login... ')
sys.stdout.flush()
chrome.connect(config['LOGIN']['ACCOUNT'],
               config['LOGIN']['PASSWORD'])
print('\033[92mOK\033[0m')


print('Retrieving operation... ')
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