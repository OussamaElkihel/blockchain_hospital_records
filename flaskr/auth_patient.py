import functools, logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth_patient', __name__, url_prefix='/auth_patient')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO patient (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Patient {username} is already registered."
            else:
                return redirect(url_for("auth_patient.login"))

        flash(error)

    return render_template('auth_patient/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM patient WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index_patient'))

        flash(error)

    return render_template('auth_patient/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        current_app.logger.info('g.user not set')
    else:
        current_app.logger.info('user_id = %d', user_id)
        g.user = get_db().execute(
            'SELECT * FROM patient WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_patient.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth_patient.login'))

        return view(**kwargs)

    return wrapped_view