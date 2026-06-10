import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.irsvqmtkwmrokpfhschk:Cti2026Passwor@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة',
    'affairs': 'شؤون المتدربين' # أضفنا هذا ليتعرف عليه النظام
}

available_slots = ['08:00', '09:00', '10:00', '11:00', '12:00', '01:00', '02:00', '03:00']

# تعريف نموذج البيانات
class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    days = db.Column(db.Text, nullable=False)
    slots = db.Column(db.Text, nullable=False)

def get_schedule_db_dict():
    schedules = Schedule.query.all()
    db_dict = {}
    for s in schedules:
        db_dict[s.target_name] = {
            'type': s.entity_type, 'dept': s.dept,
            'days': s.days.split(',') if s.days else [],
            'slots': s.slots.split(',') if s.slots else []
        }
    return db_dict

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
    return render_template('dashboard.html', departments=departments, schedule_db=get_schedule_db_dict(), available_slots=available_slots)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    return redirect(url_for('admin_dashboard'))

@app.route('/add_department', methods=['POST'])
def add_department():
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# هذا المسار هو الذي كان يسبب الـ 404
@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    return render_template('select_time.html', entity_id=entity_id, departments=departments, schedule_db=get_schedule_db_dict(), available_slots=available_slots)

@app.route('/book', methods=['POST'])
def book():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
