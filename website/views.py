from flask import Blueprint, render_template, request, redirect, url_for
from .models import Event
from . import db
main_bp = Blueprint('main', __name__)

# Assessment Code that needs to be changed

@main_bp.route('/')
def index():
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)


@main_bp.route('/search')
def search():
    if request.args['search'] and request.args['search'] != "":
        print(request.args['search'])
        query = "%" + request.args['search'] + "%"
        events = db.session.scalars(db.select(Event)).where(
            Event.description.like(query))
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = db.get_or_404(Event, event_id)
    return render_template('events.html', event=event)