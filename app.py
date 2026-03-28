from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import os
from config import Config
from models import db, User, Vendor, Booking, Review, Message
from datetime import datetime, date
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
import google.generativeai as genai

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ─── Auth Decorators ─────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                flash('Unauthorized access.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.context_processor
def inject_unread_counts():
    if 'user_id' in session:
        from sqlalchemy import func
        unread_counts = {}
        total_unread = 0
        unreads = db.session.query(Message.sender_id, func.count(Message.id))\
                    .filter_by(receiver_id=session['user_id'], is_read=False)\
                    .group_by(Message.sender_id).all()
        for sender, count in unreads:
            unread_counts[sender] = count
            total_unread += count
        return {'unread_counts': unread_counts, 'total_unread': total_unread}
    return {}

# ─── Public Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/role-select')
def role_select():
    return render_template('role_select.html')

@app.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if role not in ('customer', 'vendor'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup', role=role))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup', role=role))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = user.name
        session['email'] = user.email

        if role == 'vendor':
            flash('Account created! Please complete your vendor profile.', 'success')
            return redirect(url_for('vendor_profile_edit'))

        flash('Account created! Welcome aboard.', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('signup.html', role=role)

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if role not in ('customer', 'vendor'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email, role=role).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['email'] = user.email
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('customer_dashboard') if role == 'customer' else url_for('vendor_dashboard'))

        flash('Invalid email or password.', 'danger')
    return render_template('login.html', role=role)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ─── Customer Routes ──────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
@role_required('customer')
def customer_dashboard():
    recent = Booking.query.filter_by(customer_id=session['user_id']).order_by(Booking.created_at.desc()).limit(5).all()
    total = Booking.query.filter_by(customer_id=session['user_id']).count()
    return render_template('customer_dashboard.html', recent=recent, total=total)

@app.route('/vendors')
@login_required
@role_required('customer')
def vendors():
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    query = Vendor.query
    if category:
        query = query.filter(Vendor.category == category)
    if location:
        query = query.filter(Vendor.location.ilike(f'%{location}%'))
    vendor_list = query.all()
    categories = [r[0] for r in db.session.query(Vendor.category).distinct().all()]
    locations = [r[0] for r in db.session.query(Vendor.location).distinct().all()]
    return render_template('vendors.html', vendors=vendor_list, categories=categories,
                           locations=locations, selected_category=category, selected_location=location)

@app.route('/book/<int:vendor_id>', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def book_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    if request.method == 'POST':
        event_date_str = request.form['event_date']
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('book_vendor', vendor_id=vendor_id))

        if event_date < date.today():
            flash('Event date cannot be in the past.', 'danger')
            return redirect(url_for('book_vendor', vendor_id=vendor_id))

        booking = Booking(
            customer_id=session['user_id'],
            vendor_id=vendor_id,
            event_date=event_date,
            status='pending',
            total_price=vendor.price
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('booking_history'))

    return render_template('booking.html', vendor=vendor, today=date.today().strftime('%Y-%m-%d'))

@app.route('/bookings')
@login_required
@role_required('customer')
def booking_history():
    bookings = Booking.query.filter_by(customer_id=session['user_id']).order_by(Booking.created_at.desc()).all()
    return render_template('booking_history.html', bookings=bookings)

@app.route('/api/chat', methods=['POST'])
@login_required
@role_required('customer')
def api_chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"reply": "Please ask a question!"})

    # Optional: We construct some vendor info from the DB to help the AI answer DB-related questions
    vendors = Vendor.query.all()
    vendor_context = "Available Vendors in our DB:\n"
    for v in vendors:
        vendor_context += f"- Vendor: {v.vendor_name}, Category: {v.category}, Location: {v.location}, Price: ₹{v.price}, Rating: {v.rating}/5.0\n"

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"reply": "I'm sorry, I cannot generate ideas right now because GEMINI_API_KEY is not configured."})
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""You are a helpful event planning assistant for the Event Booking platform.
If the user's question relates to vendors, pricing, or bookings (e.g., "suggest some lowcost decoration vendor", "suggest some vendor who is in my hometown"), use the following vendor information to suggest matching options.
{vendor_context}

IMPORTANT RULES FOR VENDORS:
1. If the user mentions their "native", "hometown", or a specific location (e.g., "saravanampatti is my native"), extract that location.
2. Search the provided vendor list for that location. If you find matches, suggest them.
3. If there are NO vendors matching their exact location in the list, politely inform them that we currently don't have vendors in that specific area, and optionally suggest vendors from other locations.
4. DO NOT make up or hallucinate vendors that are not explicitly listed in the 'Available Vendors in our DB' section above.

If the user asks a general question like "suggest some decoration idea", provide a generated, creative, and thoughtful answer rather than a generic default. Do not say "For decorations, we highly recommend focusing on floral arrangements" unless it actually fits the prompt naturally. Feel free to come up with completely unique themes or decoration ideas.

The response should be polite, friendly, and concise. 
IMPORTANT FORMATTING RULES:
- Format your response using HTML tags for readability (e.g. <br>, <b> for bold, <i> for italics, <ul><li> for lists).
- Do NOT use markdown like ** or * or #.
- Start directly with the answer, no <p> tags enclosing the entire thing if not needed.

User's query: "{user_message}"
"""
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print("Error with Gemini AI:", e)
        # Fallback if Gemini fails or is not configured
        return jsonify({"reply": "I'm sorry, my AI features are currently unavailable. Please try checking the 'Browse Vendors' page from your dashboard!"})

@app.route('/chatbot')
@login_required
@role_required('customer')
def chatbot():
    return render_template('chatbot.html')


@app.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def leave_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != session['user_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('booking_history'))
    if booking.review:
        flash('You have already reviewed this booking.', 'info')
        return redirect(url_for('booking_history'))
    if booking.status != 'confirmed':
        flash('You can only review confirmed bookings.', 'warning')
        return redirect(url_for('booking_history'))

    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form.get('comment', '').strip()
        review = Review(booking_id=booking_id, rating=rating, comment=comment)
        db.session.add(review)

        # Recalculate vendor average rating
        vendor = booking.vendor
        all_ratings = [r.rating for b in vendor.bookings if b.review for r in [b.review]]
        all_ratings.append(rating)
        vendor.rating = round(sum(all_ratings) / len(all_ratings), 1)

        db.session.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('booking_history'))

    return render_template('review.html', booking=booking)

# ─── Vendor Routes ────────────────────────────────────────────────────────────

@app.route('/vendor/dashboard')
@login_required
@role_required('vendor')
def vendor_dashboard():
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    bookings = []
    stats = {'total': 0, 'pending': 0, 'confirmed': 0, 'cancelled': 0, 'revenue': 0}
    if vendor:
        bookings = Booking.query.filter_by(vendor_id=vendor.id).order_by(Booking.created_at.desc()).all()
        stats['total'] = len(bookings)
        stats['pending'] = sum(1 for b in bookings if b.status == 'pending')
        stats['confirmed'] = sum(1 for b in bookings if b.status == 'confirmed')
        stats['cancelled'] = sum(1 for b in bookings if b.status == 'cancelled')
        stats['revenue'] = sum(b.total_price for b in bookings if b.status == 'confirmed')
    return render_template('vendor_dashboard.html', vendor=vendor, bookings=bookings, stats=stats)

@app.route('/vendor/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def vendor_profile_edit():
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if request.method == 'POST':
        if not vendor:
            vendor = Vendor(user_id=session['user_id'])
            db.session.add(vendor)
        vendor.vendor_name = request.form['vendor_name'].strip()
        vendor.category = request.form['category'].strip()
        vendor.location = request.form['location'].strip()
        vendor.price = float(request.form['price'])
        vendor.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))
    return render_template('vendor_profile.html', vendor=vendor)

@app.route('/vendor/booking/<int:booking_id>/<action>')
@login_required
@role_required('vendor')
def update_booking(booking_id, action):
    booking = Booking.query.get_or_404(booking_id)
    vendor = Vendor.query.filter_by(user_id=session['user_id']).first()
    if not vendor or booking.vendor_id != vendor.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('vendor_dashboard'))
    if action == 'confirm' and booking.status == 'pending':
        booking.status = 'confirmed'
        flash('Booking confirmed.', 'success')
    elif action == 'cancel' and booking.status == 'pending':
        booking.status = 'cancelled'
        flash('Booking cancelled.', 'info')
    db.session.commit()
    return redirect(url_for('vendor_dashboard'))

# ─── Messaging Routes ─────────────────────────────────────────────────────────

@app.route('/chat/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def chat(receiver_id):
    receiver = User.query.get_or_404(receiver_id)
    sender_id = session['user_id']
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat', receiver_id=receiver_id))
    
    # Get all messages between the current user and the receiver
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == sender_id, Message.receiver_id == receiver_id),
            db.and_(Message.sender_id == receiver_id, Message.receiver_id == sender_id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark incoming messages as read
    unread_msgs = [m for m in messages if m.receiver_id == sender_id and not m.is_read]
    if unread_msgs:
        for m in unread_msgs:
            m.is_read = True
        db.session.commit()
    
    return render_template('chat.html', receiver=receiver, messages=messages)

@app.route('/chat/delete/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id == session['user_id']:
        db.session.delete(msg)
        db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/vendor/messages')
@login_required
@role_required('vendor')
def vendor_messages():
    # Find all unique customers who have sent messages to this vendor, or this vendor sent to
    vendor_id = session['user_id']
    received_msgs = Message.query.filter_by(receiver_id=vendor_id).all()
    sent_msgs = Message.query.filter_by(sender_id=vendor_id).all()
    
    user_ids = set([m.sender_id for m in received_msgs] + [m.receiver_id for m in sent_msgs])
    if vendor_id in user_ids:
        user_ids.remove(vendor_id)
        
    contacts = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
    
    return render_template('vendor_messages.html', contacts=contacts)


# ─── Seed & Init ──────────────────────────────────────────────────────────────

def seed_data():
    if User.query.first():
        return

    # Sample customers
    c1 = User(name='Alice Johnson', email='alice@example.com', role='customer')
    c1.set_password('password123')
    c2 = User(name='Bob Smith', email='bob@example.com', role='customer')
    c2.set_password('password123')

    # Sample vendors (from prototype vendors_data.py)
    v_users = [
        ('Royal Palace', 'royalpalace@example.com', 'Venue', 'Mumbai', 300000),
        ('Grand Caterers', 'grandcatering@example.com', 'Catering', 'Delhi', 150000),
        ('SnapMagic Studio', 'snapmagic@example.com', 'Photography', 'Bangalore', 50000),
        ('Bloom & Glow', 'bloomglow@example.com', 'Decoration', 'Chennai', 60000),
        ('Sound Waves DJ', 'soundwaves@example.com', 'Entertainment', 'Hyderabad', 40000),
    ]

    descriptions = {
        'Royal Palace': 'Luxury wedding venue with AC halls, valet parking, bridal suites, premium ambience',
        'Grand Caterers': 'Premium multi-cuisine catering with live counters and custom menus',
        'SnapMagic Studio': 'Candid photography, cinematic videos, drone coverage',
        'Bloom & Glow': 'Floral decorations, theme-based stage setup, premium lighting',
        'Sound Waves DJ': 'DJ, sound systems, intelligent lighting',
    }

    ratings = {'Royal Palace': 4.9, 'Grand Caterers': 4.7, 'SnapMagic Studio': 4.8,
               'Bloom & Glow': 4.6, 'Sound Waves DJ': 4.5}

    db.session.add_all([c1, c2])
    db.session.commit()

    for vname, vemail, vcat, vloc, vprice in v_users:
        vu = User(name=vname, email=vemail, role='vendor')
        vu.set_password('password123')
        db.session.add(vu)
        db.session.commit()
        v = Vendor(user_id=vu.id, vendor_name=vname, category=vcat, location=vloc,
                   price=vprice, description=descriptions[vname], rating=ratings[vname])
        db.session.add(v)
    db.session.commit()
    print("✅ Seed data inserted.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True)
