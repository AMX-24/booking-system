from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

ADMIN_USERNAME = "admin_cti"
ADMIN_PASSWORD = "cti_2026"

# تحويل الأوقات لتصبح فترات (من - إلى)
AVAILABLE_SLOTS = [
    '08:00 AM - 08:30 AM', '08:30 AM - 09:00 AM', '09:00 AM - 09:30 AM',
    '09:30 AM - 10:00 AM', '10:00 AM - 10:30 AM', '10:30 AM - 11:00 AM',
    '11:00 AM - 11:30 AM', '11:30 AM - 12:00 PM', '12:00 PM - 12:30 PM',
    '12:30 PM - 01:00 PM', '01:00 PM - 01:30 PM', '01:30 PM - 02:00 PM',
    '02:00 PM - 02:30 PM', '02:30 PM - 03:00 PM'
]

departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

bookings_db = {}

schedule_db = {
    'شؤون المتدربين': {'type': 'affairs', 'dept': 'affairs_admin', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 5, 'slots': AVAILABLE_SLOTS[0:6]},
    
    'رئيس قسم الحاسب الآلي': {'type': 'head', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم الاتصالات': {'type': 'head', 'dept': 'communications', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:8]},
    'رئيس قسم الإلكترونيات': {'type': 'head', 'dept': 'electronics', 'days': ['sun', 'tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'رئيس قسم المواد العامة': {'type': 'head', 'dept': 'general', 'days': ['mon', 'tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:8]},

    'م. بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'capacity': 2, 'slots': AVAILABLE_SLOTS[1:5]},
    'م. تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'م. تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'capacity': 3, 'slots': AVAILABLE_SLOTS[4:9]},
    
    'م. ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'م. أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    
    'م. احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'capacity': 2, 'slots': AVAILABLE_SLOTS[1:4]},
    'م. امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    
    'م. اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'م. أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
}

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
        
    stats = {
        'total_departments': len(departments),
        'total_staff': len(schedule_db),
        'total_bookings': sum(bookings_db.values())
    }
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db, available_slots=AVAILABLE_SLOTS, stats=stats)

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    dept_id = request.form.get('dept_id').strip().lower()
    dept_name = request.form.get('dept_name').strip()
    
    if dept_id and dept_name:
        if dept_id not in departments:
            departments[dept_id] = dept_name
            head_title = f"رئيس {dept_name}"
            schedule_db[head_title] = {
                'type': 'head',
                'dept': dept_id,
                'days': ['sun', 'tue'],
                'capacity': 1,
                'slots': AVAILABLE_SLOTS[0:2]
            }
            flash(f'تم إضافة {dept_name} بنجاح!', 'success')
        else:
            flash('رمز القسم موجود مسبقاً!', 'danger')
    return redirect(url_for('admin_dashboard'))

# ---- الميزة الجديدة (تعديل الأقسام) ----
@app.route('/admin/edit_department', methods=['POST'])
def edit_department():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    dept_id = request.form.get('dept_id')
    new_name = request.form.get('new_name').strip()
    
    if dept_id in departments and new_name:
        departments[dept_id] = new_name
        flash(f'تم تعديل اسم القسم إلى ({new_name}) بنجاح!', 'success')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    target_name = request.form.get('target_name')
    chosen_days = request.form.getlist('days')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    capacity = int(request.form.get('capacity', 1))
    
    if target_name in schedule_db:
        schedule_db[target_name]['days'] = chosen_days
        schedule_db[target_name]['capacity'] = capacity
        
        if start_time and end_time:
            try:
                start_idx = AVAILABLE_SLOTS.index(start_time)
                end_idx = AVAILABLE_SLOTS.index(end_time)
                if start_idx <= end_idx:
                    schedule_db[target_name]['slots'] = AVAILABLE_SLOTS[start_idx:end_idx+1]
                else:
                    flash('تنبيه: وقت البداية يجب أن يكون قبل وقت النهاية!', 'danger')
                    return redirect(url_for('admin_dashboard'))
            except ValueError:
                pass
                
        flash(f'تم حفظ السعة الاستيعابية ({capacity}) وتعديلات المواعيد لـ ({target_name}) بنجاح!', 'success')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    titles = {'affairs': 'شؤون المتدربين', 'head': 'رؤساء الأقسام', 'faculty': 'أعضاء هيئة التدريس'}
    return render_template('select_time.html', entity_id=entity_id, entity_name=titles.get(entity_id, 'المسؤول'), departments=departments, schedule_db=schedule_db)

@
