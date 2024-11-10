from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth_provider import login_required_provider
from flaskr.db import get_db

bp = Blueprint('provider', __name__)

@bp.route('/provider')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT id, username'
        ' FROM patient'
    ).fetchall()
    return render_template('blog_provider/index_provider.html', posts=posts)

@bp.route('/<int:patient_id>/create', methods=('GET', 'POST'))
@login_required_provider
def create(patient_id):
    initialize_permission(g.user['id'], patient_id)
    
    if not verify_permission(patient_id):
        flash("You don't have permission to create a record for this patient.")
        return redirect(url_for('provider.index'))
    
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        condition = request.form['condition']
        treatment = request.form['treatment']
        error = None

        if not symptoms:
            error = 'Symptoms are required.'

        if not condition:
            error = 'Condition is required.'

        if not treatment:
            error = 'Treatment is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO records (symptoms, condition, treatment, author_id, patient_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (symptoms, condition, treatment, g.user['id'], patient_id)
            )
            db.execute(
                'UPDATE patient SET has_record = ?'
                ' WHERE id = ?',
                (1, patient_id)
            )
            db.commit()
            return redirect(url_for('provider.index'))

    return render_template('blog_patient/create.html', patient_id=patient_id)

def get_post(id, check_author=True):
    post = get_db().execute(
        ' SELECT r.id, symptoms, condition, treatment, created, author_id '
        ' FROM records r JOIN provider pr ON r.author_id = pr.id '
        ' JOIN patient pa ON r.patient_id = pa.id '
        ' WHERE pa.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Record id {id} doesn't exist.")

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required_provider
def update(id):
    initialize_permission(g.user['id'], id)
    
    if not verify_permission(id):
        flash("You don't have permission to update this record for this patient.")
        return redirect(url_for('provider.index'))
    
    post = get_post(id)

    if request.method == 'POST':
        symptoms = request.form['symptoms']
        condition = request.form['condition']
        treatment = request.form['treatment']
        error = None

        if not symptoms:
            symptoms = post['symptoms']

        if not condition:
            condition = post['condition']

        if not treatment:
            treatment = post['treatment']

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE records SET symptoms = ?, condition = ?, treatment = ?'
                ' WHERE patient_id = ?',
                (symptoms, condition, treatment, id)
            )
            db.commit()
            return redirect(url_for('provider.index'))

    return render_template('blog_patient/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required_provider
def delete(id):
    #get_post(id)
    db = get_db()
    db.execute('DELETE FROM records WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('provider.index'))

@bp.route('/see_records/<int:id>', methods=('GET', 'POST'))
@login_required_provider
def see_records(id):
    initialize_permission(g.user['id'], id)
    
    if not verify_permission(id):
        flash("You don't have permission to see the records for this patient.")
        return redirect(url_for('provider.index'))
    
    post = get_post(id)
    return render_template('blog_patient/text.html', post=post)

def verify_permission(patient_id):
    db = get_db()
    perm_query = db.execute(
        'SELECT perm FROM permission WHERE author_id = ? AND patient_id = ?', 
        (g.user['id'], patient_id)
    ).fetchone()

    if perm_query is not None and perm_query['perm']:
        return True
    else:
        return False

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

