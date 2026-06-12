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

schedule_db = {
    'شؤون المتدربين': {'type': 'affairs', 'dept': 'affairs_admin', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 5, 'slots': AVAILABLE_SLOTS[0:6]},
    'رئيس قسم الحاسب الآلي': {'type': 'head', 'dept': 'computer', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم الاتصالات': {'type': 'head', 'dept': 'communications', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم الإلكترونيات': {'type': 'head', 'dept': 'electronics', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'رئيس قسم المواد العامة': {'type': 'head', 'dept': 'general', 'days': ['sun', 'mon', 'tue', 'wed', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},

    # ==================== قسم الإلكترونيات ====================
    'اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'أيمن كيفي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'أيمن بنجر': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'جابر يماني': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'جميل الجهني': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'حاتم الردادي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'حاتم الزهراني': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'حسن بادويل': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'حسين المكرمي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'خالد حجازي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'رمزي مهدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'سعود المطيري': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'سعود الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'سعود خوتنلي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'سعيد ابو عسيس': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'سلطان العتيبي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'صالح الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'طارق الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'ظافر الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'عبدالرحمن الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'عبدالله غرسان': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'عواض الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'فايز الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'فهد العامودي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'فوزي جلالة': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'محمد صباغ': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'محمد الرفاعي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'محمد عشري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'هيثم نايته': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'يزيد الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},

    # ==================== قسم الاتصالات ====================
    'احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'إيمن صائغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'بدر الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'رضا الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'سعيد ظافر': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'سامي قرامي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'سعيد عبدالرحيم': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'عمر الصايغ': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'عيد الحربي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'عيسى السقاف': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'ماجد السريحي': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'ماهر نحاس': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'محمد العلياني': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'محمد سلامي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'منصور الحازمي': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'وليد جمعة': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'ياسر مياجي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},

    # ==================== قسم الحاسب الآلي ====================
    'ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'احمد العمري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'أحمد رشاد': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'احمد عنقاوي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'أيمن العبيدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'بندر الثقفي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'بندر محمد العويضي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'ثامر عطيه الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'جمعان الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'جميل الخليفي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'حسن المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'حسين احمد باداود': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'حمد الشهابي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'حامد الشيخ': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'حامد الشمراني': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'خالد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'خليل ال صمع': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'سالم الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'سلطان ال مغلف': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'سلمان الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'صالح الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'عادل الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'عبدالرحمن المنتشري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'عبدالرحمن الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'عبدالله الحازمي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'عبدالله السهيمي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'عبدالله الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'عبدالله ناصر': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'عبدالهادي المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'عبيد الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'فايز شافعي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'فهد السميري': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'محمد العرياني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'محمد الشريف': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'منصور الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'موسى المحمادي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'وليد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'ياسر الحبشان': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},

    # ==================== قسم المواد العامة ====================
    'بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'خالد السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'خالد الزهراني': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'رامي حكمي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'سامر فطاني': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'عبدالعزيز السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'عبدالله القحطاني': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'عبدالله البشري': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'عبدالله الرفاعي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]},
    'علي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:6]},
    'علي الشهري': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:8]},
    'عمر رزق الله': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:4]},
    'فهيد المطيري': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:6]},
    'فواز الحربي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[4:9]},
    'فيصل الحارثي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[1:5]},
    'محمد ناجي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[3:7]},
    'منصور الشهراني': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'thu'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:5]},
    'هشام ابو الجدايل': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[2:7]}
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
                schedule_db[e_title] = {'type': 'custom_entity', 'dept': 'general_admin', 'days': [], 'capacity': 1, 'slots': []}
            flash(f'تم إضافة جهة الحجز ({e_title}) بنجاح!', 'success')
        else:
            flash('الرمز التعريفي للجهة موجود مسبقاً!', 'danger')
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
        if entity_id in ['affairs', 'head', 'faculty']:
            flash('لا يمكن حذف الجهات الأساسية المدمجة في هيكل النظام!', 'danger')
        else:
            e_title = main_entities[entity_id]['title']
            del main_entities[entity_id]
            if e_title in schedule_db:
                del schedule_db[e_title]
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
            schedule_db[head_title] = {'type': 'head', 'dept': dept_id, 'days': ['sun', 'tue'], 'capacity': 1, 'slots': AVAILABLE_SLOTS[0:2]}
            flash(f'تم إضافة {dept_name} بنجاح!', 'success')
        else:
            flash('رمز القسم موجود مسبقاً!', 'danger')
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
        for staff in staff_to_delete:
            del schedule_db[staff]
        flash(f'تم حذف ({dept_name}) وجميع الكوادر المرتبطة به بنجاح!', 'success')
    else:
        flash('القسم غير موجود!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_staff', methods=['POST'])
def add_staff():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    staff_name = request.form.get('staff_name').strip()
    dept_id = request.form.get('dept_id')
    staff_type = request.form.get('staff_type')
    if staff_name and dept_id:
        if staff_name in schedule_db:
            flash('هذا الاسم موجود مسبقاً في النظام!', 'danger')
        else:
            schedule_db[staff_name] = {'type': staff_type, 'dept': dept_id, 'days': [], 'capacity': 1, 'slots': []}
            flash(f'تم إضافة ({staff_name}) وربطه بالقسم بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_staff', methods=['POST'])
def edit_staff():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    old_name = request.form.get('old_staff_name')
    new_name = request.form.get('new_staff_name').strip()
    dept_id = request.form.get('dept_id')
    staff_type = request.form.get('staff_type')
    
    if old_name in schedule_db and new_name and dept_id:
        staff_data = schedule_db.pop(old_name)
        staff_data['dept'] = dept_id
        staff_data['type'] = staff_type
        schedule_db[new_name] = staff_data
        flash(f'تم تعديل بيانات ({new_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_staff/<staff_name>', methods=['POST'])
def delete_staff(staff_name):
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    if staff_name in schedule_db:
        del schedule_db[staff_name]
        flash(f'تم حذف ({staff_name}) من النظام بنجاح!', 'success')
    else:
        flash('العضو غير موجود!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
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
        flash(f'تم حفظ السعة ({capacity}) وتعديلات المواعيد لـ ({target_name}) بنجاح!', 'success')
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
    if day_name not in info['days']: return '<span class="text-danger fw-bold small">عذراً، هذا اليوم غير متاح للمقابلة حالياً!</span>'
        
    capacity_limit = info.get('capacity', 1)
    html_output = '<div class="row g-2">'
    for slot in info['slots']:
        current_bookings = bookings_db.get((target, date_str, slot), 0)
        if current_bookings < capacity_limit:
            html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-primary slot-btn w-100 p-2" onclick="selectSlot(\'{slot}\', this)">{slot}</button></div>'
        else:
            html_output += f'<div class="col-md-6 col-12"><button type="button" class="btn btn-outline-danger w-100 p-2" disabled>{slot} <br><small class="fw-bold">(ممتلئ)</small></button></div>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    student_name = request.form.get('student_name')
    student_id = request.form.get('student_id')
    student_email = request.form.get('student_email')
    target_staff = request.form.get('target')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    
    if not booking_time:
        flash('الرجاء اختيار وقت محدد من الساعات المتاحة لإتمام الحجز!', 'danger')
        return redirect(url_for('home'))
        
    capacity_limit = schedule_db.get(target_staff, {}).get('capacity', 1)
    current_bookings = bookings_db.get((target_staff, booking_date, booking_time), 0)
    
    if current_bookings >= capacity_limit:
        flash('عذراً، لقد اكتملت السعة الاستيعابية لهذا الموعد قبل قليل! الرجاء اختيار موعد آخر.', 'danger')
        return redirect(url_for('home'))
        
    bookings_db[(target_staff, booking_date, booking_time)] = current_bookings + 1
    
    dept_id = schedule_db.get(target_staff, {}).get('dept', '')
    dept_name = departments.get(dept_id, 'إدارة الكلية')
    if target_staff == 'شؤون المتدربين' or schedule_db.get(target_staff, {}).get('type') == 'custom_entity':
        dept_name = 'إدارة الكلية / الجهات الرئيسية'
        
    success_data = {'student_name': student_name, 'student_id': student_id, 'department': dept_name, 'target': target_staff, 'date': booking_date, 'time': booking_time}
    return render_template('success.html', data=success_data)

if __name__ == '__main__':
    app.run(debug=True)
