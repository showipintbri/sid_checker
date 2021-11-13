import sqlite3 as sql
import os.path
from flask import Flask, render_template, request
import waitress

# Variables
db_name = './database.db'

### Flask app

app = Flask(__name__)

def db_check(sid_id):
    if os.path.exists(db_name) == False:
        print('ERROR: Can\'t find DB file')
    else:
        conn = sql.connect(db_name)
        cur = conn.cursor()
        try:
            var = cur.execute('''SELECT sid, rule, ref FROM sids WHERE sid=?;''', (sid_id,))
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
#         print(f'POST: {sid_id}')
        rows = db_check(sid_id)
        if rows != []:
            return render_template('results.html', rows=rows)
        else:
            return render_template('error.html', sid_id=sid_id)
    elif request.method == 'GET':
        sid_id = request.args.get('sid_id')
#         print(f'GET: {sid_id}')
        db_check(sid_id)
        rows = db_check(sid_id)
        if rows != []:
            return render_template('results.html', rows=rows)
        else:
            return render_template('error.html', sid_id=sid_id)
    else:
        print('ERROR:1b something when wrong')


if __name__ == '__main__':
#     app.run(host='0.0.0.0')
    waitress.serve(app, host='0.0.0.0' port=5000)
