
# ARGUMENT PARSER #############################################

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("conf", help="Path to config.ini") 
args = parser.parse_args()

# MODULES #####################################################

import numpy as np
import pymysql
from scrapper import browser, md5_hash
from mail import sendMail
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

# RETRIEVE OPERATIONS #########################################

try:
    sql = pymysql.connect(**sql_config)
except pymysql.OperationalError as err:
    print('Erreur de connexion')
else:
    cursor = sql.cursor()
    
    # Retrieveing last 10 op
    cursor.execute('SELECT date_record,date_value,date_desc,type,description,debit,credit FROM (SELECT * FROM ' + config['SQL']['TABLE'] + ' ORDER BY id DESC LIMIT 10) as t1')
    result = np.asarray(cursor.fetchall())
    
    # Computing MD5 hash
    md5 = md5_hash(result) 
    
    # Closing SQL connection
    cursor.close()
    sql.close()

    # Scraping operations
    print('Retrieving operation... ')
    operations, new_md5 = chrome.retrieve(config['BANK']['ACCOUNT'],md5)
    chrome.quit()
    
    sendMail(len(operations),config['MAIL']['USER'],config['MAIL']['PASSWORD'])
    
    if new_md5 == md5:
        print('Already up to date')
    else:
        print('')
        print('%i operations added' % (len(operations)))
        
        try:
            sql = pymysql.connect(**sql_config)
        except pymysql.OperationalError as err:
            print('Erreur de connexion')
        else:
            cursor = sql.cursor()
            
            # Pushing new op to database
            sys.stdout.write('Pushing to database... ')
            sys.stdout.flush()

            cursor.executemany('INSERT INTO ' + config['SQL']['TABLE'] + ' (date_record,date_value,date_desc,type,description,debit,credit) VALUES (%s, %s, %s, %s, %s, %s, %s)', list(reversed(operations)))
            sql.commit()
            
            print('\033[92mOK\033[0m')
            
            # Computing missing year
            sys.stdout.write('Computing missing years... ')
            sys.stdout.flush()
            
            cursor.execute('SELECT max(id),max(year) from ref_year')
            year = np.asarray(cursor.fetchall())

            cursor.execute('SELECT * from scraping where id >= ' + str(year[0][0]))
            scraping = pd.DataFrame(np.asarray(cursor.fetchall()))
            scraping.columns = np.asarray(cursor.description)[:,0]

            i = 'date_record'

            year_ = scraping[i].str.split('/').str[1]
            year_ = (year_.shift(1) > year_).cumsum() + year[0][1]

            vals = [[int(i),j] for j,i in zip(year_[1:],scraping['id'][1:].values)]

            # Pushing years in ref_year            
            if len(vals):
                cursor.executemany("insert into ref_year(id, year) values (%s, %s)", vals )
                sql.commit()
    
            print('\033[92mOK\033[0m')
    
            # Closing sql connection
            cursor.close()
            sql.close()
            print('\033[92mOK\033[0m')