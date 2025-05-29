from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import or_
from datetime import date
from .models import Event, Category
from .forms import CommentForm
from . import db

main_bp = Blueprint('main', __name__)

# Homepage Route
@main_bp.route('/')
def index():
    events = db.session.scalars(
        db.select(Event).where(Event.end_date >= date.today())
    ).all()
    return render_template('index.html', events=events)

# Search Route with fallback and category lookup
@main_bp.route('/search')
def search():
    search_term = request.args.get('search', '').strip()
    if search_term:
        query = f"%{search_term}%"
        stmt = (
            db.select(Event)
            .join(Category)
            .where(
                or_(
                    Event.event_name.ilike(query),
                    Event.event_location.ilike(query),
                    Event.event_description.ilike(query),
                    Category.name.ilike(query)
                ),
                Event.end_date >= date.today()
            )
        )
        events = db.session.scalars(stmt).all()

        if not events:
            flash("No results found.", "warning")
            events = db.session.scalars(
                db.select(Event).where(Event.end_date >= date.today())
            ).all()
            return render_template('index.html', events=events, cleared=True)

        return render_template('index.html', events=events, cleared=False)

    return redirect(url_for('main.index'))

# Event Detail Page
@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = db.get_or_404(Event, event_id)
    form = CommentForm()
    return render_template(
        'experiences/show.html',
        event=event,
        form=form,
        user_authenticated=current_user.is_authenticated
    )
