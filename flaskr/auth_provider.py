import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth_provider', __name__, url_prefix='/auth_provider')

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
                    "INSERT INTO provider (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Provider {username} is already registered."
            else:
                return redirect(url_for("auth_provider.login_provider"))

        flash(error)

    return render_template('auth_provider/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login_provider():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM provider WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('provider.index'))

        flash(error)

    return render_template('auth_provider/login.html')

@bp.before_app_request
def load_logged_in_provider():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM provider WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout_provider():
    session.clear()
    return redirect(url_for('auth_provider.login_provider'))

def login_required_provider(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth_provider.login_provider'))

        return view(**kwargs)

    return wrapped_view