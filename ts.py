from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from time_sheet.auth import login_required
from time_sheet.db import get_db
import sys

bp = Blueprint('ts', __name__)
@login_required
@bp.route('/')
def index():
    db = get_db()
    uid = g.user['id']
    query = 'SELECT id, date, content from ts where user_id = ' + str(uid)
    tse = db.execute(query).fetchall()
    return render_template('ts/index.html', tse=tse)

@login_required
@bp.route('/filter', methods=('POST',))
def filter():
    m = request.form['month']
    y = request.form['year']
    print()
    if int(m) < 10:
        m = '0' + m
    db = get_db()
    uid = g.user['id']
    query = 'SELECT id, date, content from ts where user_id = ' + str(uid) + ' and date like "' + y + '-' + m  + '%"' 
    print(query, file=sys.stderr)
    tse = db.execute(query).fetchall()
    return render_template('ts/index.html', tse=tse)

@login_required
@bp.route('/employer_index')
def employer_index():
    db = get_db()
    query = 'select date content, username from ts,user where user.id = ts.user_id';
    tse = db.execute(query).fetchall()
    return render_template('ts/employer_index.html', tse=tse)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        content = request.form['content']
        date = request.form['date']
        db.execute(
                'INSERT INTO ts (date, content, user_id)'
                ' VALUES (?, ?, ?)',
                (date, content, g.user['id'])
        )
        db.commit()
        return redirect(url_for('ts.index'))

    return render_template('ts/create.html')


def get_ts(id):
    ts = get_db().execute(
        'SELECT id, date, content, user_id from ts'
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
        content = request.form['content']
        date = request.form['date']
        db.execute(
            'UPDATE ts SET content = ?, date = ?'
            ' WHERE id = ?',
            (content, date, id)
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
