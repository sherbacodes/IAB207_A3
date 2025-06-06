from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import or_
from datetime import date, datetime
from .models import Event, Category, Booking, Comment
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

# Orders Page
@main_bp.route('/orders')
@login_required
def orders():
    bookings = db.session.query(Booking).filter_by(user_id=current_user.id).all()
    return render_template('orders.html', bookings=bookings)

@main_bp.route('/order/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def manage_order(booking_id):
    booking = db.get_or_404(Booking, booking_id)

    # Prevent access to other users' bookings
    if booking.user_id != current_user.id:
        flash("You do not have permission to view this order.", "danger")
        return redirect(url_for('main.orders'))

    event = db.session.scalar(db.select(Event).where(Event.id == booking.event_id))
    form = CommentForm()

    if request.method == 'POST':
        if 'cancel' in request.form:
            db.session.delete(booking)
            db.session.commit()
            flash("Booking cancelled successfully.", "info")
            return redirect(url_for('main.orders'))
        elif form.validate_on_submit():
            new_comment = form.content.data
            comment = Comment(
                content=new_comment,
                user_id=current_user.id,
                event_id=event.id,
                date=datetime.utcnow()
            )
            db.session.add(comment)
            db.session.commit()
            flash("Comment posted successfully.", "success")
            return redirect(url_for('main.manage_order', booking_id=booking.id))

    return render_template(
        'order_manage.html',
        event=event,
        booking=booking,
        form=form
    )