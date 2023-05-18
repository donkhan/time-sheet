from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from time_sheet.auth import login_required
from time_sheet.db import get_db
import sys
from datetime import datetime

bp = Blueprint('ts', __name__)
@login_required
@bp.route('/')
def index():
    db = get_db()
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
        employees = db.execute('SELECT username,id from user where role == "employee"')
    return render_template('ts/index.html', tse=tse, m = m,y = today.year, role=role, employees = employees, eid=-1)

@login_required
@bp.route('/filter', methods=('POST',))
def filter():
    m = request.form['month']
    y = request.form['year']
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
    return render_template('ts/index.html', tse=tse, m=m, y = y, role=role, employees = employees, eid=eid)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print(request.form, file=sys.stderr)
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
    print(ts, file=sys.stderr)
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'UPDATE ts SET content = ?, date = ?, hours = ?, type = ?'
            ' WHERE id = ?',
            (request.form['content'], request.form['date'], request.form['hours'], request.form['type'], id)
        )
        db.commit()
        return redirect(url_for('ts.index'))
    print("rendering template ", file=sys.stderr)
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