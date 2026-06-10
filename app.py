import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# هذا هو الرابط المحدث الذي يربط مشروعك مباشرة بقاعدة بيانات سوبابيز
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Cti_Secure_Db_2026_Pass!@db.irsvqmtkwmrokpfhschk.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_USERNAME = "admin_cti"
ADMIN_PASSWORD = "cti_2026"

AVAILABLE_SLOTS = [
    '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM',
    '02:00 PM', '02:30 PM', '03:00 PM'
]

departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    target_name = db.Column(db.String(100), unique=True, nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    days = db.Column(db.Text, nullable=False)
    slots = db.Column(db.Text, nullable=False)

def get_schedule_db_dict():
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

@app.route('/')
def home():
    return render_template('index.html', departments=departments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', departments=departments, schedule_db=get_schedule_db_dict(), available_slots=AVAILABLE_SLOTS)

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    target_name = request.form.get('target_name')
    chosen_days = ",".join(request.form.getlist('days'))
    chosen_slots = ",".join(request.form.getlist('slots'))
    
    record = Schedule.query.filter_by(target_name=target_name).first()
    if record:
        record.days = chosen_days
        record.slots = chosen_slots
        db.session.commit()
        flash(f'تم حفظ التعديلات لـ ({target_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    if entity_id == 'affairs':
        entity_name = 'شؤون المتدربين'
    elif entity_id == 'head':
        entity_name = 'رئيس القسم'
    else:
        entity_name = 'أعضاء هيئة التدريس'
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=departments, schedule_db=get_schedule_db_dict())

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    schedule_db = get_schedule_db_dict()
    if not target or target not in schedule_db:
        return ''
    info = schedule_db[target]
    if day_name not in info['days']:
        return '<span class="text-danger fw-bold small">عذراً، هذا اليوم غير متاح!</span>'
    html_output = '<div class="d-flex flex-wrap justify-content-center gap-2">'
    for slot in info['slots']:
        html_output += f'<button type="button" class="btn btn-outline-primary slot-btn btn-sm" onclick="selectSlot(\'{slot}\')">{slot}</button>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    student_name = request.form.get('student_name')
    student_id = request.form.get('student_id')
    flash(f'تم تسجيل حجز الموعد للمتدرب {student_name} بنجاح!', 'success')
    return redirect(url_for('home'))

def init_db():
    with app.app_context():
        db.create_all()
        # إضافة بيانات أولية في حال كانت القاعدة فارغة
        if Schedule.query.count() == 0:
            initial_data = [
                Schedule(target_name='شؤون المتدربين', entity_type='affairs', dept='general', days='sun,mon,tue,wed,thu', slots='08:00 AM,09:30 AM,11:00 AM'),
                Schedule(target_name='رئيس قسم الحاسب الآلي', entity_type='head', dept='computer', days='sun,tue', slots='09:00 AM,10:30 AM'),
                Schedule(target_name='رئيس قسم الاتصالات', entity_type='head', dept='communications', days='mon,wed', slots='10:00 AM,11:30 AM')
            ]
            db.session.bulk_save_objects(initial_data)
            db.session.commit()

init_db()

if __name__ == '__main__':
    app.run(debug=True)
