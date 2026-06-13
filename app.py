from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

ADMIN_USERNAME = "admin_cte"
ADMIN_PASSWORD = "cte_2026"

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

schedule_db = {
    'شؤون المتدربين': {'type': 'affairs', 'dept': 'affairs_admin', 'days': [], 'capacity': 5, 'slots': []},
    'رئيس قسم الحاسب الآلي': {'type': 'head', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'رئيس قسم الاتصالات': {'type': 'head', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'رئيس قسم الإلكترونيات': {'type': 'head', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'رئيس قسم المواد العامة': {'type': 'head', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},

    # ==================== قسم الإلكترونيات ====================
    'اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'أيمن كيفي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'أيمن بنجر': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'جابر يماني': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'جميل الجهني': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'حاتم الردادي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'حاتم الزهراني': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'حسن بادويل': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'حسين المكرمي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'خالد حجازي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'رمزي مهدي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'سعود المطيري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'سعود الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'سعود خوتنلي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'سعيد ابو عسيس': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'سلطان العتيبي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'صالح الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'طارق الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'ظافر الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالرحمن الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله غرسان': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'عواض الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'فايز الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'فهد العامودي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'فوزي جلالة': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'محمد صباغ': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'محمد الرفاعي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'محمد عشري': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'هيثم نايته': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},
    'يزيد الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': [], 'capacity': 1, 'slots': []},

    # ==================== قسم الاتصالات ====================
    'احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'إيمن صائغ': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'بدر الجهني': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'رضا الجهني': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'سعيد ظافر': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'سامي قرامي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'سعيد عبدالرحيم': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'عمر الصايغ': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'عيد الحربي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'عيسى السقاف': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'ماجد السريحي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'ماهر نحاس': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'محمد العلياني': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'محمد سلامي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'منصور الحازمي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'وليد جمعة': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},
    'ياسر مياجي': {'type': 'faculty', 'dept': 'communications', 'days': [], 'capacity': 1, 'slots': []},

    # ==================== قسم الحاسب الآلي ====================
    'ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'احمد العمري': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'أحمد رشاد': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'احمد عنقاوي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'أيمن العبيدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'بندر الثقفي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'بندر محمد العويضي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'ثامر عطيه الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'جمعان الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'جميل الخليفي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'حسن المالكي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'حسين احمد باداود': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'حمد الشهابي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'حامد الشيخ': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'حامد الشمراني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'خالد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'خليل ال صمع': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'سالم الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'سلطان ال مغلف': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'سلمان الشهري': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'صالح الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عادل الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالرحمن المنتشري': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالرحمن الحربي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله الحازمي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله السهيمي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله الشهري': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله ناصر': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالهادي المالكي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'عبيد الحربي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'فايز شافعي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'فهد السميري': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'محمد العرياني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'محمد الشريف': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'منصور الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'موسى المحمادي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'وليد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},
    'ياسر الحبشان': {'type': 'faculty', 'dept': 'computer', 'days': [], 'capacity': 1, 'slots': []},

    # ==================== قسم المواد العامة ====================
    'بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'خالد السلمي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'خالد الزهراني': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'رامي حكمي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'سامر فطاني': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالعزيز السلمي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله القحطاني': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله البشري': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'عبدالله الرفاعي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'علي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'علي الشهري': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'عمر رزق الله': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'فهيد المطيري': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'فواز الحربي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'فيصل الحارثي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'محمد ناجي': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'منصور الشهراني': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []},
    'هشام ابو الجدايل': {'type': 'faculty', 'dept': 'general', 'days': [], 'capacity': 1, 'slots': []}
}

# إضافة إيميل افتراضي لأي دكتور ما عنده إيميل مسجل مسبقاً
for name, info in schedule_db.items():
    if 'email' not in info:
        info['email'] = 'doctor@tvtc.edu.sa'

@app.route('/')
def home():
    return render_template('index.html', main_entities=main_entities)

# ==================== دخول وإدارة لوحة التحكم المركزية ====================
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

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    stats = {
        'total_departments': len(departments),
        'total_staff': len(schedule_db),
        'total_bookings': len(detailed_bookings_list),
        'total_entities': len(main_entities)
    }
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db, main_entities=main_entities, time_markers=TIME_MARKERS, stats=stats, detailed_bookings=detailed_bookings_list)

# ==================== نظام دخول أعضاء هيئة التدريس ====================
@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        for name, info in schedule_db.items():
            if info.get('type') in ['faculty', 'head'] and info.get('email', '').lower() == email:
                session['staff_logged_in'] = name 
                return redirect(url_for('staff_dashboard'))
        flash('البريد الإلكتروني غير صحيح أو غير مسجل في النظام!', 'danger')
    return render_template('staff_portal.html', view='login')

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'staff_logged_in' not in session: return redirect(url_for('staff_login'))
    staff_name = session['staff_logged_in']
    my_bookings = [b for b in detailed_bookings_list if b['target'] == staff_name]
    return render_template('staff_portal.html', view='dashboard', staff_name=staff_name, bookings=my_bookings)

@app.route('/staff_logout')
def staff_logout():
    session.pop('staff_logged_in', None)
    return redirect(url_for('home'))

# ==================== الإجراءات الإدارية (حذف وإضافة وتعديل) ====================
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
            flash(f'تم إلغاء حجز المتدرب ذو الرقم ({student_id}) وإعادة إتاحة المقعد بنجاح!', 'success')
            break
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_entity', methods=['POST'])
def add_entity():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    e_id = request.form.get('e_id').strip().lower()
    e_title = request.form.get('e_title').strip()
    e_icon = request.form.get('e_icon').strip()
    e_desc = request.form.get('e_desc').strip()
    if e_id and e_title:
        if e_id not in main_entities:
            main_entities[e_id] = {'title': e_title, 'icon': e_icon, 'desc': e_desc}
            if e_title not in schedule_db:
                schedule_db[e_title] = {'type': 'custom_entity', 'dept': 'general_admin', 'email': 'admin@tvtc.edu.sa', 'days': [], 'capacity': 1, 'slots': []}
            flash(f'تم إضافة جهة الحجز ({e_title}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_entity', methods=['POST'])
def edit_entity():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    e_id = request.form.get('e_id')
    e_title = request.form.get('new_title').strip()
    e_icon = request.form.get('new_icon').strip()
    e_desc = request.form.get('new_desc').strip()
    if e_id in main_entities:
        old_title = main_entities[e_id]['title']
        main_entities[e_id] = {'title': e_title, 'icon': e_icon, 'desc': e_desc}
        if old_title != e_title and old_title in schedule_db:
            schedule_db[e_title] = schedule_db.pop(old_title)
        flash('تم تعديل بيانات الجهة بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_entity/<entity_id>', methods=['POST'])
def delete_entity(entity_id):
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    if entity_id in main_entities:
        e_title = main_entities[entity_id]['title']
        del main_entities[entity_id]
        if e_title in schedule_db: del schedule_db[e_title]
        flash(f'تم حذف جهة ({e_title}) نهائياً!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    dept_id = request.form.get('dept_id').strip().lower()
    dept_name = request.form.get('dept_name').strip()
    if dept_id and dept_name:
        if dept_id not in departments:
            departments[dept_id] = dept_name
            head_title = f"رئيس {dept_name}"
            schedule_db[head_title] = {'type': 'head', 'dept': dept_id, 'email': f'head_{dept_id}@tvtc.edu.sa', 'days': [], 'capacity': 1, 'slots': []}
            flash(f'تم إضافة {dept_name} بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_department', methods=['POST'])
def edit_department():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    dept_id = request.form.get('dept_id')
    new_name = request.form.get('new_name').strip()
    if dept_id in departments and new_name:
        departments[dept_id] = new_name
        flash(f'تم تعديل اسم القسم إلى ({new_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_department/<dept_id>', methods=['POST'])
def delete_department(dept_id):
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    if dept_id in departments:
        dept_name = departments[dept_id]
        del departments[dept_id]
        staff_to_delete = [staff_name for staff_name, info in schedule_db.items() if info.get('dept') == dept_id]
        for staff in staff_to_delete: del schedule_db[staff]
        flash(f'تم حذف ({dept_name}) وجميع الكوادر المرتبطة به بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

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
            flash(f'تم إضافة ({staff_name}) وربطه بالقسم بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_staff', methods=['POST'])
def edit_staff():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    old_name = request.form.get('old_staff_name')
    new_name = request.form.get('new_staff_name').strip()
    dept_id = request.form.get('dept_id')
    staff_type = request.form.get('staff_type')
    staff_email = request.form.get('staff_email').strip() # استقبال الإيميل المعدل
    
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
        flash(f'تم حذف ({staff_name}) من النظام بنجاح!', 'success')
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
            except ValueError:
                continue
        flash(f'تم تحديث الجدول الأسبوعي بنجاح للمسؤول ({target_name})!', 'success')
    return redirect(url_for('admin_dashboard'))

# ==================== عمليات الحجز والواجهة للمتدرب ====================
@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    if entity_id not in main_entities: return redirect(url_for('home'))
    entity_name = main_entities[entity_id]['title']
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=departments, schedule_db=schedule_db)

@app.route('/get_staff_by_dept', methods=['POST'])
def get_staff_by_dept():
    dept_id = request.form.get('dept_id')
    filtered_staff = {name: info for name, info in schedule_db.items() if info.get('dept') == dept_id}
    html = '<option value="">-- اختر الدكتور / المهندس --</option>'
    for name in filtered_staff.keys(): html += f'<option value="{name}">{name}</option>'
    return html

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    date_str = request.form.get('date_str')
    if not target or target not in schedule_db: return ''
    info = schedule_db[target]
    
    weekly_schedule = info.get('weekly_schedule', {})
    if day_name in weekly_schedule and weekly_schedule[day_name]:
        slots_data = weekly_schedule[day_name]
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
    return '<span class="text-danger fw-bold small">عذراً، لا توجد مواعيد متاحة في هذا اليوم!</span>'

@app.route('/book', methods=['POST'])
def book():
    student_name = request.form.get('student_name')
    student_id = request.form.get('student_id')
    student_email = request.form.get('student_email')
    target_staff = request.form.get('target')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    
    if not booking_time: return redirect(url_for('home'))
    info = schedule_db.get(target_staff, {})
    capacity_limit = info.get('capacity', 1)
    
    try:
        date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
        days_map = {6: 'sun', 0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat'}
        day_name = days_map[date_obj.weekday()]
        if 'weekly_schedule' in info and day_name in info['weekly_schedule'] and booking_time in info['weekly_schedule'][day_name]:
            capacity_limit = info['weekly_schedule'][day_name][booking_time]
    except: pass
        
    current_bookings = bookings_db.get((target_staff, booking_date, booking_time), 0)
    if current_bookings >= capacity_limit: return redirect(url_for('home'))
        
    bookings_db[(target_staff, booking_date, booking_time)] = current_bookings + 1
    detailed_bookings_list.append({
        'student_name': student_name, 'student_id': student_id, 'student_email': student_email,
        'target': target_staff, 'date': booking_date, 'time': booking_time
    })
    
    dept_id = info.get('dept', '')
    dept_name = departments.get(dept_id, 'إدارة الكلية')
    success_data = {'student_name': student_name, 'student_id': student_id, 'department': dept_name, 'target': target_staff, 'date': booking_date, 'time': booking_time}
    return render_template('success.html', data=success_data)

if __name__ == '__main__':
    app.run(debug=True)
