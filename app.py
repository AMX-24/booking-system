import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# الرابط المحدث بكلمة المرور الجديدة
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cti2026Passwor@db.irsvqmtkwmrokpfhschk.supabase.co:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# تعريف الأقسام لحل مشكلة UndefinedError
departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    days = db.Column(db.Text, nullable=False)
    slots = db.Column(db.Text, nullable=False)

def get_schedule_db_dict():
    try:
        schedules = Schedule.query.all()
        db_dict = {}
        for s in schedules:
            db_dict[s.target_name] = {
                'type': s.entity_type,
                'dept': s.dept,
                'days': [day.strip() for day in s.days.split(',')] if s.days else [],
                'slots': [slot.strip() for slot in s.slots.split(',')] if s.slots else []
            }
        return db_dict
    except Exception as e:
        print(f"ERROR: Database fetch error: {e}")
        return {}

@app.route('/')
def home():
    return render_template('index.html', departments=departments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "admin_cti" and request.form.get('password') == "cti_2026":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    return render_template('dashboard.html', departments=departments, schedule_db=get_schedule_db_dict())

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    return render_template('select_time.html', entity_id=entity_id, departments=departments, schedule_db=get_schedule_db_dict())

@app.route('/book', methods=['POST'])
def book():
    flash('تم حجز الموعد بنجاح!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
