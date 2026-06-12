from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

ADMIN_USERNAME = "admin_cti"
ADMIN_PASSWORD = "cti_2026"

AVAILABLE_SLOTS = [
    '08:00 AM - 08:30 AM', '08:30 AM - 09:00 AM', '09:00 AM - 09:30 AM',
    '09:30 AM - 10:00 AM', '10:00 AM - 10:30 AM', '10:30 AM - 11:00 AM',
    '11:00 AM - 11:30 AM', '11:30 AM - 12:00 PM', '12:00 PM - 12:30 PM',
    '12:30 PM - 01:00 PM', '01:00 PM - 01:30 PM', '01:30 PM - 02:00 PM',
    '02:00 PM - 02:30 PM', '02:30 PM - 03:00 PM'
]

main_entities = {
    'affairs': {'title': 'شؤون المتدربين', 'icon': '👤', 'desc': 'حجز موعد لمراجعة خدمات المتدربين والملفات'},
    'head': {'title': 'رئيس القسم', 'icon': '👔', 'desc': 'حجز موعد لمقابلة رئيس القسم الأكاديمي المختص'},
    'faculty': {'title': 'أعضاء هيئة التدريس', 'icon': '👨‍🏫', 'desc': 'حجز موعد مع المهندسين والدكاترة والمحاضرين'}
}

departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

bookings_db = {}

# (قاعدة البيانات للأسماء تبقى كما هي من الكود السابق، لن أطيلها هنا اختصاراً ولكن أبقها لديك كما هي)
# للتبسيط هنا سأضع بيانات مختصرة، **أنت احتفظ باللستة الطويلة التي عندك في كودك**
schedule_db = {
    'شؤون المتدربين': {'type': 'affairs', 'dept': 'affairs_admin', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 5, 'slots': AVAILABLE_SLOTS[0:6]},
    'رئيس قسم الحاسب الآلي': {'type': 'head', 'dept': 'computer', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم الاتصالات': {'type': 'head', 'dept': 'communications', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم الإلكترونيات': {'type': 'head', 'dept': 'electronics', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم المواد العامة': {'type': 'head', 'dept': 'general', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    # (ضع باقي الدكاترة الـ 100 هنا كما كانوا في النسخة السابقة)
}

@app.route('/')
def home():
    return render_template('index.html', main_entities=main_entities)

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
        'total_bookings': sum(bookings_db.values()),
        'total_entities': len(main_entities)
    }
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db, main_entities=main_entities, available_slots=AVAILABLE_SLOTS, stats=stats)

# --- (دوال الإضافة والتعديل والحذف للأقسام والجهات والكادر تبقى كما هي) ---

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    
    target_name = request.form.get('target_name')
    spec_date = request.form.get('spec_date')
    spec_day = request.form.get('spec_day') # اليوم المختار يدوياً
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    capacity = int(request.form.get('capacity', 1))
    
    if target_name in schedule_db and spec_date and start_time and end_time:
        if 'custom_dates' not in schedule_db[target_name]:
            schedule_db[target_name]['custom_dates'] = {}
            
        if spec_date not in schedule_db[target_name]['custom_dates']:
            schedule_db[target_name]['custom_dates'][spec_date] = {}
            
        try:
            start_idx = AVAILABLE_SLOTS.index(start_time)
            end_idx = AVAILABLE_SLOTS.index(end_time)
            if start_idx <= end_idx:
                # توليد فترات المواعيد بين البداية والنهاية للتاريخ المختار
                for slot in AVAILABLE_SLOTS[start_idx:end_idx+1]:
                    schedule_db[target_name]['custom_dates'][spec_date][slot] = capacity
                flash(f'تم حفظ المواعيد لـ ({target_name}) بتاريخ {spec_date} من {start_time} إلى {end_time} بنجاح!', 'success')
            else:
                flash('تنبيه: وقت البداية يجب أن يكون قبل وقت النهاية!', 'danger')
        except ValueError:
            pass
    else:
        flash('تنبيه: الرجاء تعبئة جميع الحقول بشكل صحيح!', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    if entity_id not in main_entities:
        return redirect(url_for('home'))
    entity_name = main_entities[entity_id]['title']
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=departments, schedule_db=schedule_db)

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    date_str = request.form.get('date_str')
    
    if not target or target not in schedule_db: return ''
    info = schedule_db[target]
    
    # التحقق من وجود مواعيد مخصصة (بالتاريخ)
    custom_dates = info.get('custom_dates', {})
    if date_str in custom_dates and custom_dates[date_str]:
        slots_data = custom_dates[date_str]
        html_output = '<div class="row g-2">'
        for slot in AVAILABLE_SLOTS:
            if slot in slots_data:
                cap = slots_data[slot]
                current_bookings = bookings_db.get((target, date_str, slot), 0)
                if current_bookings < cap:
                    html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-primary slot-btn w-100 p-2" onclick="selectSlot(\'{slot}\', this)">{slot}</button></div>'
                else:
                    html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-danger w-100 p-2" disabled>{slot} <br><small class="fw-bold">(ممتلئ)</small></button></div>'
        html_output += '</div>'
        return html_output
        
    # إذا لم يجد موعد مخصص لهذا التاريخ، يعود للجدول الافتراضي أو يرفض
    if day_name not in info.get('days', []): 
        return '<span class="text-danger fw-bold small">عذراً، لا يوجد موعد متاح لهذا اليوم!</span>'
        
    capacity_limit = info.get('capacity', 1)
    html_output = '<div class="row g-2">'
    for slot in info.get('slots', []):
        current_bookings = bookings_db.get((target, date_str, slot), 0)
        if current_bookings < capacity_limit:
            html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-primary slot-btn w-100 p-2" onclick="selectSlot(\'{slot}\', this)">{slot}</button></div>'
        else:
            html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-danger w-100 p-2" disabled>{slot} <br><small class="fw-bold">(ممتلئ)</small></button></div>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    # ... (دالة الحجز تبقى كما هي) ...
