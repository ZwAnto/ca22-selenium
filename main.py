
# ARGUMENT PARSER #############################################

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("conf", help="Path to config.ini") 
args = parser.parse_args()

# MODULES #####################################################

import numpy as np
import pymysql
from saveload import *
from scrapper import browser, md5_hash
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

sql_config = {
    'user':         config['SQL']['USERNAME'],
    'password':     config['SQL']['PASSWORD'],
    'host':         config['SQL']['HOST'],
    'database':     config['SQL']['DATABASE'],
    'port':         int(config['SQL']['PORT'])           
    }

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

try:
    sql = pymysql.connect(**sql_config)
except pymysql.OperationalError as err:
    print('Erreur de connexion')
else:
    cursor = sql.cursor()
    cursor.execute('SELECT date_record,date_value,date_desc,type,description,debit,credit FROM (SELECT * FROM ' + config['SQL']['TABLE'] + ' ORDER BY id DESC LIMIT 10) as t1')
    result = np.asarray(cursor.fetchall())
    md5 = md5_hash(result) 
    
    cursor.close()
    sql.close()

    # RETRIEVE OPERATIONS #########################################

    print('Retrieving operation... ')
    operations, new_md5 = chrome.retrieve(config['BANK']['ACCOUNT'],md5)
    chrome.quit()

    if new_md5 == md5:
        print('Already up to date')
    else:
        print('')
        print('%i operations added' % (len(operations)))

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

if os.path.isfile(config['SCRAPER']['DIR_OUT'] + 'ca22.sql'):
    try:
        sql = pymysql.connect(**sql_config)
    except pymysql.OperationalError as err:
        print('Erreur de connexion')
    else:
        cursor = sql.cursor()
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