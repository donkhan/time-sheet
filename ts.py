from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from time_sheet.auth import login_required
from time_sheet.db import get_db
import sys
from datetime import datetime

import jinja2
import pdfkit
from datetime import datetime

bp = Blueprint('ts', __name__)
@login_required
@bp.route('/list')
def list():
    db = get_db()
    if g.user is None:
        return redirect('/auth/login')
    uid = g.user['id']
    today = datetime.today()
    role = session['user_role']
    if role == 'employee':
        query = 'SELECT ts.id, date, content, user_id, hours, type, status, username from ts,user where user_id = ' + str(uid) + ' and date like "' + today.strftime("%Y-%m") + '%"' + ' and user_id = user.id '
    else:
        query = 'SELECT ts.id, date, content, user_id,hours, type, status, username from ts,user where date like "' + today.strftime("%Y-%m") + '%"' + ' and user_id = user.id'
    tse = db.execute(query).fetchall()
    m = today.month
    if m < 9:
        m = "0" + str(m)
    employees = []
    if role == 'employer':
        employees = db.execute('SELECT username,id from user where role == "employee" and user.companyId = ' + str(uid))
    return render_template('ts/index.html', tse=tse, m = m, y = today.year, role=role, 
                           employees = employees, eid=-1, years = ["2023","2024"],
                           months = get_months())

@login_required
@bp.route('/filter', methods=('POST',))
def filter():
    m = request.form['month']
    y = request.form['year']
    if int(m) < 10:
        m = "0" + m
    eid = -1
    employees = []
    db = get_db()
    uid = g.user['id']
    role = session['user_role']
    if role == 'employer':
        employees = db.execute('SELECT username,id from user where role == "employee"')
    if role == 'employee':
        query = 'SELECT ts.id, date, content, user_id, hours, type, status, username from ts,user where user_id = ' + str(uid) + ' and date like "' + y + '-' + m  + '%"'  + ' and user_id = user.id'
    else:
        query = 'SELECT ts.id, date, content, user_id, hours, type, status, username from ts,user where date like "' + y + '-' + m  + '%"'  + ' and user_id = user.id'
        eid = request.form['employee']
        if eid != "-1":
            query += ' and user.id = ' + eid
    print(query, file=sys.stderr)
    tse = db.execute(query).fetchall()
    return render_template('ts/index.html', tse=tse, m=m, y = y, role=role, 
                           employees = employees, eid=int(eid), years = ["2023","2024"],
                           months = get_months())


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        db.execute(
                'INSERT INTO ts (date, content, hours, type, status,user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (request.form['date'], request.form['content'], request.form['hours'],request.form['type'],0,g.user['id'])
        )
        db.commit()
        return redirect(url_for('ts.index'))
    return render_template('ts/create.html')


def get_ts(id):
    ts = get_db().execute(
        'SELECT id, date, content, hours, type, status, user_id from ts'
        ' WHERE ts.id = ?',
        (id,)
    ).fetchone()
    if ts is None:
        abort(404, f"Entry id {id} doesn't exist.")
    return ts

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    ts = get_ts(id)
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'UPDATE ts SET content = ?, date = ?, hours = ?, type = ?'
            ' WHERE id = ?',
            (request.form['content'], request.form['date'], request.form['hours'], request.form['type'], id)
        )
        db.commit()
        return redirect(url_for('ts.index'))
    return render_template('ts/update.html', ts=ts)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_ts(id)
    db = get_db()
    db.execute('DELETE FROM ts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('ts.index'))

@bp.route('/<int:id>/accept', methods=('POST',))
@login_required
def accept(id):
    get_ts(id)
    db = get_db()
    db.execute(
            'UPDATE ts SET status = ?'
            ' WHERE id = ?',
            (1, id)
        )
    db.commit()
    return redirect(url_for('ts.index'))

@bp.route('/<int:id>/decline', methods=('POST',))
@login_required
def decline(id):
    get_ts(id)
    db = get_db()
    db.execute(
            'UPDATE ts SET status = ?'
            ' WHERE id = ?',
            (2, id)
        )
    db.commit()
    return redirect(url_for('ts.index'))


@login_required
@bp.route('/gen_report', methods=('POST',))
def gen_report():
    m = request.form['month']
    y = request.form['year']
    no_of_dates = get_days_of_month(m,y) + 1
    w = datetime.strptime("1-" + m + "-" + y, "%d-%m-%Y").strftime('%w')
    data = []
    days = get_days_list(no_of_dates,w)
    tw = 0
    holidays = 0
    clocked_hours = 0
    leave_hours = 0
    for i in range(1, no_of_dates+1):
        d = dict()
        d['date'] = i
        d['day'] = days[i-1]
        tw += working_hours(i,m,y,days[i-1])
        holidays += holiday(i,m,y,days[i-1])
        data.append(d)
    
    db = get_db()
    uid = request.form['employee']
    if uid == "-1":
        return redirect(url_for('ts.index'))
    if int(m) < 10:
        m = "0" + m
    query = 'SELECT ts.id, date, content, user_id, hours, type, status from ts where user_id = ' + str(uid) + ' and date like "' + y + '-' + m  + '%"' 
    records = db.execute(query).fetchall()
    for record in records:
        index = int(str(record['date']).split("-")[2])
        row = data[index-1]
        row['content'] = record['content']
        if str(record['type']) == 'Leave':
            row['leave'] = record['hours']
            leave_hours += record['hours']
        else:
            row['work'] = record['hours']
            clocked_hours += record['hours']

    query = 'SELECT username,name,imgURL, url from user,company where user.id = ' + uid + ' and user.companyId = company.id'
    records = db.execute(query).fetchone()
    user_name = records[0]
    file_name = user_name + "-" + m + "-" + y + ".pdf"
    half = int(len(data)/2)
    context = {
        'name' : user_name,
        'consultancy_name' : records[1],
        'consultancy_url' : records[3],
        'img_url' : records[2],
        "data_1": data[0:half],
        "data_2": data[half:],
        "month" : get_months()[int(m)-1],
        "year": y,
        'total_working_hours': tw,
        'clocked_hours' : clocked_hours,
        'leave_hours' : leave_hours,
        'holidays' :holidays
    }
    if  records[1] == "AGNI Technologies" :
        context["data"] = data
    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template('templates/ts/agni_report.html')
    
    if records[1] == "Rizq Solutions":
        template = template_env.get_template('templates/ts/report.html')
    
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    pdfkit.from_string(output_text, 'static/' + file_name, configuration=config, css='static/style.css')
    return redirect('static/' + file_name)

def get_days_of_month(m,y):
    if m == 1 or m == 3 or m == 5 or m == 7 or m == 8 or m == 10 or m == 12:
        return 31
    if m == 2:
        return 28
    return 30

def get_days_list(no_of_dates,w):
    w = int(w)
    l = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    l = l[w:len(l)] + l[0:w]
    l = l * 5
    return l[0:no_of_dates]

def get_months():
    return ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    
def working_hours(d,m,y,w):
    if w == 'Sun' or w == 'Sat':
        return 0
    return 8

def holiday(d,m,y,w):
    if w == 'Sun' or w == 'Sat':
        return 1
    return 8