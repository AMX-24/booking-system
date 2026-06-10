from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

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

schedule_db = {
    'شؤون المتدربين': {
        'type': 'affairs',
        'dept': 'general',
        'days': ['sun', 'mon', 'tue', 'wed', 'thu'],
        'slots': ['08:00 AM', '09:30 AM', '11:00 AM']
    },
    'رئيس قسم الحاسب الآلي': {
        'type': 'head',
        'dept': 'computer',
        'days': ['sun', 'tue'],
        'slots': ['09:00 AM', '10:30 AM']
    },
    'رئيس قسم الاتصالات': {
        'type': 'head',
        'dept': 'communications',
        'days': ['mon', 'wed'],
        'slots': ['10:00 AM', '11:30 AM']
    },
    'رئيس قسم الإلكترونيات': {
        'type': 'head',
        'dept': 'electronics',
        'days': ['sun', 'tue', 'thu'],
        'slots': ['09:00 AM', '10:30 AM', '11:30 AM']
    },
    'رئيس قسم المواد العامة': {
        'type': 'head',
        'dept': 'general',
        'days': ['mon', 'tue', 'wed'],
        'slots': ['08:30 AM', '10:00 AM', '12:00 PM']
    },

    'م. بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:30 PM']},
    'م. خالد السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. خالد الزهراني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. رامي حكمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سامر فطاني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. عبدالعزيز السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'thu'], 'slots': ['08:30 AM', '11:00 AM']},
    'م. عبدالله القحطاني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. عبدالله البشري': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عبدالله الرفاعي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. علي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. علي الشهري': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. عمر رزق الله': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. فهيد المطيري': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. فواز الحربي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'mon'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. فيصل الحارثي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. محمد ناجي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. منصور الشهراني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. هشام ابو الجدايل': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},

    'م. ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. احمد العمري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:30 PM']},
    'م. أحمد رشاد': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. أحمد عنقاوي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. أيمن العبيدي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. بندر الثقفي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. بندر محمد العويضي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'slots': ['08:30 AM', '11:00 AM']},
    'م. ثامر عطيه الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. جمعان الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. جميل الخليفي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. حسن المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. حسين احمد باداود': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. حمد الشهابي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. حامد الشيخ': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. حامد الشمراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. خالد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. خليل ال صمع': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. سالم الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سلطان ال مغلف': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. سلمان الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:30 PM']},
    'م. صالح الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. عادل الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. عبدالرحمن المنتشري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عبدالرحمن الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. عبدالله الحازمي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'slots': ['08:30 AM', '11:00 AM']},
    'م. عبدالله السهيمي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. عبدالله الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عبدالله ناصر': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. عبدالهادي المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. عبيد الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. فايز شافعي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. فهد السميري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. محمد العرياني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. محمد الشريف': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. منصور الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. موسى المحمادي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. وليد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. ياسر الحبشان': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:30 PM']},

    'م. احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},
    'د. إيمن صائغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:30 PM']},
    'م. بدر الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. رضا الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. سعيد ظافر': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سامي قرامي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. سعيد عبدالرحيم': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'thu'], 'slots': ['08:30 AM', '11:00 AM']},
    'م. عمر الصايغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. عيد الحربي': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عيسى السقاف': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. ماجد السريحي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. ماهر نحاس': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. محمد العلياني': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. محمد سلامي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. منصور الحازمي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'mon'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. وليد جمعة': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. ياسر مياجي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},

    'م. اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'د. أيمن كيفي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. أيمن بنجر': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:30 AM']},
    'م. جابر يماني': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. جميل الجهني': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. حاتم الردادي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. حاتم الزهراني': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. حسن بادويل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. حسين المكرمي': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '11:30 AM']},
    'م. خالد حجازي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. رمزي مهدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سعود المطيري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. سعود الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سعود خوتنلي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. سعيد ابو عسيس': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. سلطان العتيبي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['09:00 AM', '11:30 AM']},
    'م. صالح الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. طارق الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. ظافر الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عبدالرحمن الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': ['09:00 AM', '11:00 AM']},  # تم إصلاح الخطأ هنا
    'م. عبدالله غرسان': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. عواض الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['10:00 AM', '01:00 PM']},
    'م. فايز الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. فهد العامودي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': ['09:30 AM', '11:30 AM']},
    'م. فوزي جلالة': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. محمد صباغ': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '12:00 PM']},
    'م. محمد الرفاعي': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. محمد عشري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['09:00 AM', '11:00 AM']},
    'م. هيثم نايته': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '10:00 AM']},
    'م. يزيد الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '01:00 PM']}
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
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db, available_slots=AVAILABLE_SLOTS)

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
                'slots': ['08:00 AM', '09:00 AM']
            }
            flash(f'تم إضافة {dept_name} بنجاح للرئيسية والبطاقات الإدارية!', 'success')
        else:
            flash('رمز القسم موجود مسبقاً!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    target_name = request.form.get('target_name')
    chosen_days = request.form.getlist('days')
    chosen_slots = request.form.getlist('slots')
    
    if target_name in schedule_db:
        schedule_db[target_name]['days'] = chosen_days
        schedule_db[target_name]['slots'] = chosen_slots
        flash(f'تم حفظ تعديلات المواعيد والأيام لـ ({target_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    # نحدد الاسم بناءً على النوع المختار للـ Entity
    if entity_id == 'affairs':
        entity_name = 'شؤون المتدربين'
    elif entity_id == 'head':
        entity_name = 'رئيس القسم'
    else:
        entity_name = 'أعضاء هيئة التدريس'
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=departments, schedule_db=schedule_db)

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    
    if not target or target not in schedule_db:
        return ''
        
    info = schedule_db[target]
    if day_name not in info['days']:
        return '<span class="text-danger fw-bold small">عذراً، هذا اليوم غير متاح للمقابلة حالياً!</span>'
        
    html_output = '<div class="d-flex flex-wrap justify-content-center gap-2">'
    for slot in info['slots']:
        html_output += f'<button type="button" class="btn btn-outline-primary slot-btn btn-sm" onclick="selectSlot(\'{slot}\')">{slot}</button>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    student_name = request.form.get('student_name')
    student_id = request.form.get('student_id')
    flash(f'تم تسجيل حجز الموعد بنجاح للمتدرب {student_name} (الرقم الأكاديمي: {student_id})!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
