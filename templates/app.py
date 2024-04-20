from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
from urllib.parse import urlencode
import json
import os
import random
import string
from datetime import datetime

app = Flask(__name__)
mysql = MySQL(app)

app.secret_key = os.urandom(24).hex()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ecom'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def getUserDataById(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s",(user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return user_data

app.jinja_env.globals.update(getUserDataById=getUserDataById) 

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    msg=''
    if session.get('admin_loggedin'):
        return redirect(url_for('admin_dashboard'))
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM admin WHERE email = %s AND password = %s",(email,password))
            data = cur.fetchone()
            if data:
                session['admin-email'] = email
                session['admin_loggedin'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                msg = 'Please enter the correct details.'
                return render_template('admin/index.html', msg=msg)
        return render_template('admin/index.html')
    
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_loggedin', None)
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('admin_loggedin'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user_transactions ORDER BY id DESC LIMIT 10")
        recent_transactions = cursor.fetchall()
        return render_template('admin/dashboard.html', recent_transactions=recent_transactions)
    else:
        return redirect(url_for('admin_login'))