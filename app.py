from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

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

TIME_MARKERS = [
    '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM',
    '02:00 PM', '02:30 PM', '03:00 PM'
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
detailed_bookings_list = [] 

# تم اختصار قائمة الدكاترة هنا لسهولة القراءة، (أبقِ القائمة الطويلة التي لديك كما هي، فقط تأكد من وضع هذا الكود البرمجي تحتها)
schedule_db = {
    'شؤون المتدربين': {'type': 'affairs', 'dept': 'affairs_admin', 'email': 'affairs@tvtc.edu.sa', 'days': [], 'capacity': 5, 'slots': []},
    'خالد الغامدي': {'type': 'faculty', 'dept': 'computer', 'email': 'k.alghamdi@tvtc.edu.sa', 'days': [], 'capacity': 1, 'slots': []},
    # (ضع بقية الدكاترة الـ 100 هنا كما كانوا في كودك السابق)
}

# كود ذكي: يضيف إيميل افتراضي لكل دكتور موجود مسبقاً عشان ما تتعب في تعديلهم واحد واحد (تقدر تعدلهم من لوحة التحكم لاحقاً)
for name, info in schedule_db.items():
    if 'email' not in info:
        info['email'] = 'doctor@tvtc.edu.sa'

@app.route('/')
def home():
    return render_template('index.html', main_entities=main_entities)

# ==================== نظام دخول الإدارة ====================
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
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

# ==================== نظام دخول الدكاترة (الجديد) ====================
@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        # البحث عن الدكتور بالإيميل
        for name, info in schedule_db.items():
            if info.get('type') in ['faculty', 'head'] and info.get('email', '').lower() == email:
                session['staff_logged_in'] = name # تسجيل دخول الدكتور باسمه
                return redirect(url_for('staff_dashboard'))
        flash('البريد الإلكتروني غير صحيح أو غير مسجل في النظام!', 'danger')
    return render_template('staff_portal.html', view='login')

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'staff_logged_in' not in session: return redirect(url_for('staff_login'))
    staff_name = session['staff_logged_in']
    
    # جلب الحجوزات الخاصة بهذا الدكتور فقط
    my_bookings = [b for b in detailed_bookings_list if b['target'] == staff_name]
    
    return render_template('staff_portal.html', view='dashboard', staff_name=staff_name, bookings=my_bookings)

@app.route('/staff_logout')
def staff_logout():
    session.pop('staff_logged_in', None)
    return redirect(url_for('home'))

# ==================== لوحة تحكم الإدارة ====================
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    stats = {
        'total_departments': len(departments), 'total_staff': len(schedule_db),
        'total_bookings': len(detailed_bookings_list), 'total_entities': len(main_entities)
    }
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db, main_entities=main_entities, time_markers=TIME_MARKERS, stats=stats, detailed_bookings=detailed_bookings_list)

@app.route('/admin/delete_booking', methods=['POST'])
def delete_booking():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    student_id = request.form.get('student_id')
    target = request.form.get('target')
    date = request.form.get('date')
    time = request.form.get('time')
    global detailed_bookings_list, bookings_db
    for b in detailed_bookings_list:
        if b['student_id'] == student_id and b['target'] == target and b['date'] == date and b['time'] == time:
            detailed_bookings_list.remove(b)
            if (target, date, time) in bookings_db:
                bookings_db[(target, date, time)] = max(0, bookings_db[(target, date, time)] - 1)
            flash(f'تم إلغاء حجز المتدرب ({student_id}) وإعادة إتاحة المقعد!', 'success')
            break
    return redirect(url_for('admin_dashboard'))

# ... (دوال الإضافة والتعديل للجهات والأقسام تبقى كما هي) ...

@app.route('/admin/add_staff', methods=['POST'])
def add_staff():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    staff_name = request.form.get('staff_name').strip()
    dept_id = request.form.get('dept_id')
    staff_type = request.form.get('staff_type')
    staff_email = request.form.get('staff_email').strip() # استقبال الإيميل
    
    if staff_name and dept_id:
        if staff_name not in schedule_db:
            schedule_db[staff_name] = {'type': staff_type, 'dept': dept_id, 'email': staff_email, 'days': [], 'capacity': 1, 'slots': []}
            flash(f'تم إضافة ({staff_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_staff', methods=['POST'])
def edit_staff():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    old_name = request.form.get('old_staff_name')
    new_name = request.form.get('new_staff_name').strip()
    dept_id = request.form.get('dept_id')
    staff_type = request.form.get('staff_type')
    staff_email = request.form.get('staff_email').strip() # استقبال الإيميل المُعدل
    
    if old_name in schedule_db and new_name and dept_id:
        staff_data = schedule_db.pop(old_name)
        staff_data['dept'] = dept_id
        staff_data['type'] = staff_type
        staff_data['email'] = staff_email
        schedule_db[new_name] = staff_data
        flash(f'تم تعديل بيانات ({new_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_staff/<staff_name>', methods=['POST'])
def delete_staff(staff_name):
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    if staff_name in schedule_db:
        del schedule_db[staff_name]
        flash(f'تم حذف ({staff_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    target_name = request.form.get('target_name')
    days_list = request.form.getlist('spec_day[]')
    starts_list = request.form.getlist('start_time[]')
    ends_list = request.form.getlist('end_time[]')
    caps_list = request.form.getlist('capacity[]')
    
    if target_name in schedule_db and days_list:
        schedule_db[target_name]['weekly_schedule'] = {}
        schedule_db[target_name]['days'] = list(set(days_list))
        
        for i in range(len(days_list)):
            day = days_list[i]
            start = starts_list[i]
            end = ends_list[i]
            cap = int(caps_list[i])
            if day not in schedule_db[target_name]['weekly_schedule']:
                schedule_db[target_name]['weekly_schedule'][day] = {}
            try:
                start_idx = TIME_MARKERS.index(start)
                end_idx = TIME_MARKERS.index(end)
                if start_idx < end_idx:
                    for slot in AVAILABLE_SLOTS[start_idx:end_idx]:
                        schedule_db[target_name]['weekly_schedule'][day][slot] = cap
            except ValueError: continue
        flash(f'تم تحديث الجدول الأسبوعي بنجاح للمسؤول ({target_name})!', 'success')
    return redirect(url_for('admin_dashboard'))

# ... (دوال الحجز الخاصة بالمتدربين تبقى كما هي بدون تغيير) ...
# (يرجى إبقاء دوال /select_time و /get_staff_by_dept و /get_slots_ajax و /book كما هي في كودك)

if __name__ == '__main__':
    app.run(debug=True)
