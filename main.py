
# ARGUMENT PARSER #############################################

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("conf", help="Path to config.ini") 
args = parser.parse_args()

# MODULES #####################################################

import numpy as np
import pymysql
from saveload import *
from scrapper import browser
import pickle
import hashlib
import pandas as pd
import configparser
import sys
import os
import re

# CONFIGURATION FILE ##########################################

sys.stdout.write('Reading config.ini... ')
sys.stdout.flush()
config = configparser.ConfigParser()
config.read(args.conf)
print('\033[92mOK\033[0m')

# BROWSER INITIALISATION ######################################

sys.stdout.write('Browser initialization... ')
sys.stdout.flush()
chrome = browser(config['CHROME']['DRIVER'])
print('\033[92mOK\033[0m')

# LOGIN #######################################################

sys.stdout.write('Login... ')
sys.stdout.flush()
chrome.connect(config['LOGIN']['ACCOUNT'],
               config['LOGIN']['PASSWORD'])
print('\033[92mOK\033[0m')

# READING CHECKSUM ############################################

if os.path.isfile(config['SCRAPER']['DIR_OUT'] + 'ca22.md5'):
    sys.stdout.write('Readig checksum... ')
    sys.stdout.flush()
    with open(config['SCRAPER']['DIR_OUT'] + 'ca22.md5','r') as f:
        md5 = f.read() 
    print('\033[92mOK\033[0m')
else:
    md5 = None

# RETRIEVE OPERATIONS #########################################

print('Retrieving operation... ')
operations, new_md5 = chrome.retrieve(config['BANK']['ACCOUNT'],md5)
chrome.quit()

if new_md5 == md5:
    print('Already up to date')
else:
    print('')
    print('%i operations added' % (len(operations)))
    with open(config['SCRAPER']['DIR_OUT'] + 'ca22.md5','w') as f:
        f.write(new_md5) 
        
# RETRIEVE OPERATIONS #########################################

    sys.stdout.write('Building SQL query... ')
    sys.stdout.flush()
    if not os.path.isfile(config['SCRAPER']['DIR_OUT'] + 'ca22.sql'):
        with open(config['SCRAPER']['DIR_OUT'] + 'ca22.sql','w') as f:
            f.write('INSERT INTO ' + config['SQL']['TABLE'] + ' (date_record,date_value,date_desc,type,description,debit,credit) VALUES ')

    with open(config['SCRAPER']['DIR_OUT'] + 'ca22.sql','a') as f:
        for i in range(len(operations)):
            a = [ '"' + i + '"' for i in operations[-(i+1)][:5]]
            if a[2] == '""':
                a[2] = a[1]
            b = [re.sub(',','.',i).strip() for i in operations[-(i+1)][5:]]
            b = [re.sub(' |\\\\','',i) for i in b]
            b = ['0' if i == '' else i for i in b ]

            f.writelines('(' + ','.join(a+b) + '),')
    print('\033[92mOK\033[0m')
    
    sys.stdout.write('Pushing to database... ')
    sys.stdout.flush()
    
    sql_config = {
    'user':         config['SQL']['USERNAME'],
    'password':     config['SQL']['PASSWORD'],
    'host':         config['SQL']['HOST'],
    'database':     config['SQL']['DATABASE'],
    'port':         int(config['SQL']['PORT'])           
    }

    try:
            sql = pymysql.connect(**sql_config)
    except pymysql.OperationalError as err:
            print('Erreur de connexion')
    else:
            cursor = sql.cursor()
            if os.path.isfile(config['SCRAPER']['DIR_OUT'] + 'ca22.sql'):
                    try:
                        with open(config['SCRAPER']['DIR_OUT'] + 'ca22.sql','r') as file:
                            query = file.read()
                        query = re.sub(',$',';',query)
                        cursor.execute(query)
                    except Exception as e:
                        cursor.close()
                        sql.close()
                        print('FAIL')
                        print(e)
                    else:
                        os.remove(config['SCRAPER']['DIR_OUT'] + 'ca22.sql')
                        sql.commit()
                        cursor.close()
                        sql.close()
                        print('\033[92mOK\033[0m')
    

        
    '''        
##### SQL #####################

print('Retrieving operation... ')
try:
    histo = load(config['SCRAPER']['OUT'])
    new_histo = chrome.retrieve(config['BANK']['ACCOUNT'],histo[:10])

    if len(new_histo):
        print('Adding %i new entries.' % len(new_histo))
        
        histo = new_histo + histo
        save(histo,config['SCRAPER']['OUT'])
        
except FileNotFoundError:
    
    histo = chrome.retrieve(config['BANK']['ACCOUNT'])
    save(histo,config['SCRAPER']['OUT'])
    
sys.stdout.write('Computing md5 hash... ')
sys.stdout.flush()
md5 = hashlib.md5(pickle.dumps(histo[:10])).hexdigest()   
with open(config['SCRAPER']['DIR_OUT'] + 'ca22.md5','w+') as f:
    f.write(md5) 
print('\033[92mOK\033[0m')

chrome.quit()
'''