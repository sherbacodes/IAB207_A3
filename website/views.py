from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from .models import Event
from .forms import CommentForm
from . import db

main_bp = Blueprint('main', __name__)

# Homepage Route
@main_bp.route('/')
def index():
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)

# Search Route
@main_bp.route('/search')
def search():
    if request.args.get('search') and request.args['search'].strip() != "":
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(
            db.select(Event).where(Event.event_name.like(query))
        ).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))

# Event Detail Page
@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = db.get_or_404(Event, event_id)
    form = CommentForm() if current_user.is_authenticated else None
    return render_template(
        'experiences/show.html',
        event=event,
        form=form,
        user_authenticated=current_user.is_authenticated
    )