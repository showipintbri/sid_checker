import sqlite3 as sql
import requests
import hashlib
import re
from zipfile import ZipFile
import os.path
import sid_checker

# Variables
filename = 'emerging-all.rules.zip'
filename_md5 = filename+'.md5'
et_url = 'https://rules.emergingthreats.net/open/suricata-5.0/'


# Create the database
if os.path.exists('./database.db') == False:
    try:
        conn = sql.connect('./database.db')
        print("Opened database successfully")
        conn.execute('CREATE TABLE sids (sid INT, rule TEXT)')
        conn.commit()
        print("Table created successfully")
        conn.close()
    except:
        pass
else:
    pass

### Define functions

# Extract
def extract(file):
    with ZipFile(file, 'r') as zip:
        zip.printdir()
        zip.extractall()
        print(f'Extracted file: {file}')


# Build Database
def build_db():
    print('NOTICE: Starting to build the Database')
    conn = sql.connect('./database.db')
    with open('emerging-all.rules', 'r') as rules:
        for line in rules.readlines():
            clean_line = line.strip('\n')
            if str(clean_line) != '':
                sid_regex = re.compile('sid:(\d+);')
                sid = sid_regex.search(str(clean_line))
                if sid != None:
                    sid_num = sid.group(1)
                    conn.execute('INSERT INTO sids VALUES (?, ?)', (int(sid_num), str(clean_line)))
                else:
                    pass
            else:
                pass
    rules.close()
    conn.commit()
    conn.close()
    print('NOTICE: Finished building the database.')
       


# Download the 'all-rules' zip file
try:
    url = et_url+filename

    dl_file = requests.get(url, allow_redirects=True)
    try:
        open('./'+filename, 'wb').write(dl_file.content)
        print(f'Wrote file to disk: {filename}')
    except:
        print('Error')
except:
    print(f'Error: Couldn\'t download the file from ET: {url}')

# Generate an MD5 of the file
try:
    hash = hashlib.md5(dl_file.content)
    file_hash = hash.hexdigest()
    print(file_hash)
except:
    print(f'Error: Couldn\'t generate an MD5 hash of the file: {filename}')

# Get the posted MD5 hash from emergingthreats
try:
    url_md5 = et_url+filename_md5

    et_md5 = requests.get(url_md5, allow_redirects=True)
    et_hash = et_md5.text.strip()
    print(et_hash)
except:
    print(f'Error: Could\'nt download the filehash file from {url_md5}')

# Compare the hashes
try:
    if str(file_hash) == str(et_hash):
        print('It\'s a Match!')
        extract(filename)
    else:
        print('ERROR: MD5\'s Don\'t Match, will not continue.')
except:
    print('Error: Couldn\'t compare, hash input error possible.')

build_db()

sid_checker.app.run()
