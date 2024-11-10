from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from flaskr.auth_patient import login_required
from flaskr.db import get_db

bp = Blueprint('patient', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT id, username '
        'FROM provider'
    ).fetchall()
    patients = db.execute(
        'SELECT id, username '
        'FROM patient'
    ).fetchall()
    return render_template('blog_patient/index_patient.html', posts=posts, patients=patients)

@bp.route('/grant_permission/provider/<int:provider_id>/patient/<int:patient_id>', methods=('GET', 'POST'))
def grant_permission(provider_id, patient_id):
    db = get_db()

    # Initialize the permission entry if it doesn't already exist
    initialize_permission(provider_id, patient_id)
    
    # Check if permission has already been granted
    perm = db.execute(
        'SELECT perm FROM permission WHERE author_id = ? AND patient_id = ?',
        (provider_id, patient_id)
    ).fetchone()
    
    if perm is not None and perm['perm']:
        flash("Permission already granted.")
        return redirect(url_for('patient.index'))
    
    current_app.logger.info('provider_id = %d and patient_id = %d', provider_id, patient_id)

    # If this is a POST request, update the permission
    if request.method == 'POST':
        db.execute(
            'UPDATE permission SET perm = ? WHERE author_id = ? AND patient_id = ?',
            (1, provider_id, patient_id)
        )
        db.commit()
        return redirect(url_for('patient.index'))

    return render_template('blog_patient/index_patient.html')

@bp.route('/remove_permission/provider/<int:provider_id>/patient/<int:patient_id>', methods=('GET', 'POST'))
def remove_permission(provider_id, patient_id):
    db = get_db()

    # Initialize the permission entry if it doesn't already exist
    initialize_permission(provider_id, patient_id)

    # Check if permission has already been removed
    perm = db.execute(
        'SELECT perm FROM permission WHERE author_id = ? AND patient_id = ?',
        (provider_id, patient_id)
    ).fetchone()
    
    if perm is not None and not perm['perm']:
        flash("Permission already removed.")
        return redirect(url_for('patient.index'))

    # If this is a POST request, update the permission to remove it
    if request.method == 'POST':
        db.execute(
            'UPDATE permission SET perm = ? WHERE author_id = ? AND patient_id = ?',
            (0, provider_id, patient_id)
        )
        db.commit()
        return redirect(url_for('patient.index'))

    return render_template('blog_patient/index_patient.html')

def initialize_permission(author_id, patient_id):
    db = get_db()
    # Check if permission entry already exists
    existing_permission = db.execute(
        'SELECT 1 FROM permission WHERE author_id = ? AND patient_id = ?',
        (author_id, patient_id)
    ).fetchone()
    
    # If no existing entry, create a new one
    if existing_permission is None:
        db.execute(
            'INSERT INTO permission (author_id, patient_id, perm) VALUES (?, ?, ?)',
            (author_id, patient_id, 0)  # Assuming `0` is the default `perm` value
        )
        db.commit()

"""
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO records (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('patient.index'))

    return render_template('blog_patient/create.html')"""
""""""
    
"""
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, symptoms, condition, treatment, created, author_id, username'
        ' FROM records p JOIN patient u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Record id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE records SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('patient.index'))

    return render_template('blog_patient/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM records WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('patient.index'))

"""