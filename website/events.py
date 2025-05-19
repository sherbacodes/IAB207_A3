from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Category
from .forms import EventManagementForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

eventbp = Blueprint('event', __name__, url_prefix='/experiences')


@eventbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    form = CommentForm() if current_user.is_authenticated else None
    return render_template(
        'experiences/show.html',
        event=event,
        form=form,
        user_authenticated=current_user.is_authenticated
    )


@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    print('Method type: ', request.method)
    form = EventManagementForm()
    form.category_id.choices = [(-1, "Select a category...")] + [
        (c.id, c.name) for c in Category.query.all()
    ]

    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        event = Event(
            event_name=form.event_name.data,
            category_id=form.category_id.data,
            event_description=form.event_description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            start_time=form.start_time.data.strftime('%H:%M'),  # stored as string
            end_time=form.end_time.data.strftime('%H:%M'),
            event_location=form.event_location.data,
            event_image=db_file_path,
            ticket_price=form.ticket_price.data,
            capacity=form.capacity.data,
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new music event', 'success')
        return redirect(url_for('event.create'))

    return render_template('experiences/create.html', form=form)


def check_upload_file(form):
    fp = form.event_image.data
    filename = secure_filename(fp.filename)
    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, 'static/img', filename)
    db_upload_path = '/static/img/' + filename
    fp.save(upload_path)
    return db_upload_path


@eventbp.route('/<id>/comment', methods=['POST'])
@login_required
def comment(id):
    form = CommentForm()
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            event=event,
            user=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added', 'success')

    return redirect(url_for('event.show', id=id))


@eventbp.route('/cancel_event/<id>', methods=['GET', 'POST'])
@login_required
def cancel_event(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if event.user_id != current_user.id:
        flash('You are not authorized to cancel this event', 'danger')
        return redirect(url_for('event.show', id=id))

    db.session.delete(event)
    db.session.commit()
    flash('Event cancelled successfully', 'success')
    return redirect(url_for('event.create'))