import sqlite3 as sql
import requests
import hashlib
import re
from zipfile import ZipFile
import os.path
# import sid_checker
from flask import Flask, render_template, request


### Define functions

# Create the database
def create_db(db_name):
    if os.path.exists(db_name) == False:
        try:
            conn = sql.connect(db_name)
            print("Opened database successfully")
            conn.execute('CREATE TABLE sids (sid INT, rule TEXT)')
            conn.commit()
            print("Table created successfully")
            conn.close()
        except:
            pass
    else:
        pass


def gen_md5(file_content):
# Generate an MD5 of the file content
# Called from Function: dl_all_rules
    try:
        hash = hashlib.md5(file_content)
        hash_digest = hash.hexdigest()
        print(hash_digest)
        return hash_digest
    except:
        print(f'Error: Couldn\'t generate an MD5 hash of the file: {filename}')
        return


def dl_all_rules(url,filename):
# Download the 'all-rules' zip file
# and generate the MD5 hash digest of the file content
    try:
        dl_file = requests.get(url, allow_redirects=True)
        try:
            open('./'+filename, 'wb').write(dl_file.content)
            print(f'Wrote file to disk: {filename}')
        except:
            print('Error')
        try:
            dl_file_hash = gen_md5(dl_file.content)
            return dl_file_hash
        except:
            print(f'ERROR: Couldn\'t generate the MD5 hash')
    except:
        print(f'Error: Couldn\'t download the file from ET: {url}')
        
  

def dl_md5(url_md5):
# Get the posted MD5 hash from emergingthreats
    try:
        et_md5 = requests.get(url_md5, allow_redirects=True)
        et_hash_digest = et_md5.text.strip()
        print(et_hash_digest)
    except:
        print(f'Error: Could\'nt download the filehash file from {url_md5}')
    return et_hash_digest
        

def extract(file):
# Extract Zip 
# Called from below function: comp_hashes
    with ZipFile(file, 'r') as zip:
        zip.printdir()
        zip.extractall()
        print(f'Extracted file: {file}')
        

def comp_hashes(file_hash,et_hash,filename):
# Compare the hashes
    try:
        if str(file_hash) == str(et_hash):
            print('It\'s a Match!')
            extract(filename)
        else:
            print('ERROR: MD5 Hashes Don\'t Match, will not continue.')
    except:
        print('Error: Couldn\'t compare, hash input error possible.')
        

# Build Database
def build_db(db_name):
    print('NOTICE: Starting to build the Database')
    conn = sql.connect(db_name)
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
       

# Variables
db_name = './database.db'
filename = 'emerging-all.rules.zip'
filename_md5 = filename+'.md5'
et_url = 'https://rules.emergingthreats.net/open/suricata-5.0/'        
url = et_url+filename
url_md5 = et_url+filename_md5


### Flask app

app = Flask(__name__)

def db_check(sid_id):
    if os.path.exists(db_name) == False:
        print('ERROR: Can\'t find DB file')
    else:
        conn = sql.connect(db_name)
        cur = conn.cursor()
        try:
            var = cur.execute('''SELECT sid, rule FROM sids WHERE sid=?;''', (sid_id,))
            rows = var.fetchall()
            cur.close()
            conn.close()
            return rows
        except:
            print('ERROR:1a something when wrong')
            cur.close()
            conn.close()
            return render_template('error.html', sid_id=sid_id) #Change this to an error page

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        sid_id = request.form['sid_id']
        print(f'POST: {sid_id}')
        rows = db_check(sid_id)
        if rows != []:
            return render_template('results.html', rows=rows)
        else:
            return render_template('error.html', sid_id=sid_id)
    elif request.method == 'GET':
        sid_id = request.args.get('sid_id')
        print(f'GET: {sid_id}')
        db_check(sid_id)
        rows = db_check(sid_id)
        if rows != []:
            return render_template('results.html', rows=rows)
        else:
            return render_template('error.html', sid_id=sid_id)
    else:
        print('ERROR:1b something when wrong')
    
def start_app():
#    app.run(debug=True)
    create_db(db_name)
    file_hash = dl_all_rules(url,filename)
    et_hash = dl_md5(url_md5)
    comp_hashes(file_hash,et_hash,filename)
    build_db(db_name)
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    start_app()
