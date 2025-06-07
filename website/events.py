from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Category, Booking
from .forms import EventManagementForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func

eventbp = Blueprint('event', __name__, url_prefix='/experiences')


@eventbp.route('/<id>', methods=['GET', 'POST'])
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    form = CommentForm() if current_user.is_authenticated else None

    if event.end_date.date() < datetime.utcnow().date() and event.event_status not in ['Cancelled', 'Inactive']:
        event.event_status = 'Inactive'
        db.session.commit()

    total_booked = db.session.query(func.sum(Booking.quantity)).filter_by(event_id=event.id).scalar() or 0
    remaining_tickets = event.capacity - total_booked

    if request.method == 'POST' and 'quantity' in request.form:
        if not current_user.is_authenticated:
            flash("You must be logged in to book tickets.", "danger")
            return redirect(url_for('auth.login'))

        quantity = int(request.form.get('quantity', 1))
        ticket_type = request.form.get('ticketType', 'general')

        if quantity < 1:
            flash("You must book at least one ticket.", "danger")
            return redirect(url_for('event.show', id=id))

        if quantity > remaining_tickets:
            flash(f"Only {remaining_tickets} tickets available. Please adjust your quantity.", "danger")
            return redirect(url_for('event.show', id=id))

        total_price = quantity * event.ticket_price

        new_booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            ticket_type=ticket_type,
            quantity=quantity,
            total_price=total_price,
            booking_date=datetime.utcnow()
        )
        db.session.add(new_booking)

        remaining_tickets -= quantity
        if remaining_tickets <= 0:
            event.event_status = 'Sold Out'

        db.session.commit()

        flash('Your tickets have been booked successfully!', 'success')
        return redirect(url_for('main.orders'))

    return render_template(
        'experiences/show.html',
        event=event,
        form=form,
        user_authenticated=current_user.is_authenticated,
        remaining_tickets=remaining_tickets
    )


@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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
            start_time=form.start_time.data,
            end_time=form.end_time.data,
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


@eventbp.route('/my-events')
@login_required
def my_events():
    today = datetime.utcnow().date()
    events = Event.query.filter_by(user_id=current_user.id).all()

    for event in events:
        event_end_date = event.end_date.date()  # ensure consistent type
        if event_end_date < today and event.event_status not in ['Cancelled', 'Inactive']:
            event.event_status = 'Inactive'

    db.session.commit()

    # Filter using .date() for correct logic
    active_events = [e for e in events if e.end_date.date() >= today]
    past_events = [e for e in events if e.end_date.date() < today]

    return render_template('experiences/my_events.html', active_events=active_events, past_events=past_events)


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


@eventbp.route('/cancel_event/<id>', methods=['POST'])
@login_required
def cancel_event(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if event.user_id != current_user.id:
        flash('You are not authorized to cancel this event', 'danger')
        return redirect(url_for('event.show', id=id))

    event.event_status = 'Cancelled'
    db.session.commit()
    flash('Event has been cancelled successfully.', 'success')
    return redirect(url_for('event.show', id=id))


@eventbp.route('/<id>/manage', methods=['GET', 'POST'])
@login_required
def manage_event(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))

    if event.user_id != current_user.id:
        flash("You are not authorized to manage this event.", "danger")
        return redirect(url_for('event.show', id=id))

    form = EventManagementForm(obj=event)
    form.category_id.choices = [(-1, "Select a category...")] + [
        (c.id, c.name) for c in Category.query.all()
    ]
    form.category_id.data = event.category_id

    total_booked = db.session.query(func.sum(Booking.quantity)).filter(Booking.event_id == event.id).scalar() or 0
    remaining_tickets = event.capacity - total_booked

    if form.validate_on_submit():
        if form.capacity.data < total_booked:
            flash(
                f"You cannot reduce the capacity below {total_booked} (already sold). "
                f"Please contact the event website for refund assistance.",
                "danger"
            )
            return render_template('experiences/manage.html', form=form, event=event, remaining_tickets=remaining_tickets)

        event.event_name = form.event_name.data
        event.category_id = form.category_id.data
        event.event_description = form.event_description.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.event_location = form.event_location.data
        event.ticket_price = form.ticket_price.data
        event.capacity = form.capacity.data

        if form.event_image.data and hasattr(form.event_image.data, 'filename') and form.event_image.data.filename:
            db_path = check_upload_file(form)
            if db_path:
                event.event_image = db_path

        # Recalculate and update event status if needed
        new_remaining = event.capacity - total_booked
        if event.event_status in ['Sold Out', 'Inactive'] and new_remaining > 0:
            event.event_status = 'Active'

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for('event.show', id=id))

    return render_template('experiences/manage.html', form=form, event=event, remaining_tickets=remaining_tickets)