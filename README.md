# Event Booking MVP

A full-stack Flask + MySQL event booking platform built from your prototype.

## What Changed from Prototype
- Removed all AI/RAG/chatbot components
- Removed static vendor mock data
- Replaced all HTML-only pages with Jinja2 templates using Flask
- Connected to MySQL via SQLAlchemy ORM
- Real authentication with hashed passwords
- Real booking/review workflow with DB persistence

## Setup Instructions

### 1. Create MySQL Database
```sql
CREATE DATABASE event_booking_db;
```

### 2. Configure Database
Edit `config.py` and update your MySQL credentials:
```python
'mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost/event_booking_db'
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```
The app runs at: **http://127.0.0.1:5000**

Database tables and sample data are created automatically on first run.

---

## Sample Login Credentials

| Role     | Email                       | Password     |
|----------|-----------------------------|--------------|
| Customer | alice@example.com           | password123  |
| Customer | bob@example.com             | password123  |
| Vendor   | royalpalace@example.com     | password123  |
| Vendor   | grandcatering@example.com   | password123  |
| Vendor   | snapmagic@example.com       | password123  |

---

## Project Structure
```
event_booking_mvp/
├── app.py              # Main Flask app + all routes
├── config.py           # DB config
├── models.py           # SQLAlchemy models (User, Vendor, Booking, Review)
├── requirements.txt
├── README.md
├── static/
│   ├── style.css       # Styling (matches prototype colors)
│   └── script.js       # Alert auto-dismiss + date validation
└── templates/
    ├── base.html
    ├── index.html
    ├── role_select.html
    ├── login.html
    ├── signup.html
    ├── customer_dashboard.html
    ├── vendors.html
    ├── booking.html
    ├── booking_history.html
    ├── review.html
    ├── vendor_dashboard.html
    └── vendor_profile.html
```
