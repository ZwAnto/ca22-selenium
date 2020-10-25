
import logging
import os
import re
import sys

import plac
import pyaml
import pymysql

from scrapper import browser, md5_hash

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s',level=logging.INFO)

def main(config_file='config.yml'):

    if not os.path.isfile(config_file):
        logging.error('File %s does not exist.', config_file)
        exit()

    # CONFIGURATION FILE ##########################################

    try:
        config = pyaml.yaml.load(open(config_file), Loader=pyaml.yaml.loader.BaseLoader)
    except Exception:
        logging.exception('Error during reading of %s', config_file)
        exit()
    else:
        logging.info('Configuration file sucessfully imported.')

    # BROWSER INITIALISATION ######################################

    try:
        chrome = browser(config['chromedriver'])
    except Exception:
        logging.exception('Error during browser initialisation.')
        exit()
    else:
        logging.info('Browser initialized sucessfully.')

    # LOGIN #######################################################

    try:
        chrome.connect(**config['login'])
    except Exception:
        logging.exception('Error during login.')
        exit()
    else:
        logging.info('Login sucessfull.')

    # RETRIEVE OPERATIONS #########################################

    try:
        sql_config = {
            'user':         config['sql']['username'],
            'password':     config['sql']['password'],
            'host':         config['sql']['host'],
            'database':     config['sql']['database'],
            'port':         int(config['sql']['port'])           
        }
        sql = pymysql.connect(**sql_config)
    except:
        logging.exception('Error during sql connection initialisation.')
        chrome.quit()
        exit()
    else:
        logging.info('SQL connection established.')
        
    # HASH #########################################

    try:
        cursor = sql.cursor()
        
        # Retrieveing last 10 op
        _ = cursor.execute('SELECT date_record,date_value,date_desc,type,description,debit,credit,date FROM (SELECT * FROM scraping ORDER BY id DESC LIMIT 10) as t1')
        result = np.asarray(cursor.fetchall())
        
        # Computing MD5 hash
        md5 = md5_hash(result) 
        logging.debug('Hash of last 10 sql entries: %s', md5)
        # Closing sql connection
        cursor.close()
    except:
        logging.exception('Error querying last 10 entries in scrapping table.')
        chrome.quit()
        sql.close()
        exit()

    # RETRIEVING

    try:
        operations, new_md5 = chrome.retrieve(config['bank_account'], md5)
        chrome.quit()
    except:
        logging.exception('Error during new operation retrieval.')
        chrome.quit()
        exit()
    else:
        logging.info('%i operations retrieved.', len(operations))



    if new_md5 == md5:
        logging.info('Database up-to-date.')
    else:
        try:
            cursor = sql.cursor()
            
            cursor.executemany('INSERT INTO scraping (date_record,date_value,date_desc,type,description,debit,credit, date) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)', list(reversed(operations)))
            sql.commit()
            
            cursor.close()
        except:
            logging.exception('Error during SQL INSERT query.')
            sql.close()
            exit()
        else:
            logging.info('Database up-to-date.')
        
    sql.close()
    exit()

if __name__ == '__main__':
    import plac; plac.call(main)
