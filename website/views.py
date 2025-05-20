from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import or_
from .models import Event, Category
from .forms import CommentForm
from . import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    events = db.session.scalars(db.select(Event)).all()
    return render_template('index.html', events=events)

@main_bp.route('/search')
def search():
    search_term = request.args.get('search', '').strip()
    if search_term:
        query = f"%{search_term}%"
        # Join with Category to search category name
        stmt = (
            db.select(Event)
            .join(Category)
            .where(
                or_(
                    Event.event_name.ilike(query),
                    Event.event_location.ilike(query),
                    Event.event_description.ilike(query),
                    Category.name.ilike(query)  # <-- search category name here
                )
            )
        )
        events = db.session.scalars(stmt).all()
        return render_template('index.html', events=events)
    else:
        return redirect(url_for('main.index'))

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