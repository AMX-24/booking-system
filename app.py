from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# حساب أدمن موحد وصلاحية واحدة للنظام كامل
ADMIN_USERNAME = "admin_cti"
ADMIN_PASSWORD = "cti_password_2026"

# دالة لتوليد الأوقات تلقائياً من 8:00 ص إلى 3:00 م بفارق نصف ساعة
def generate_default_slots():
    slots = []
    # الفترة الصباحية من 8 إلى 11:30
    for hour in [8, 9, 10, 11]:
        slots.append(f"{hour:02d}:00 AM")
        slots.append(f"{hour:02d}:30 AM")
    # فترة الظهر من 12 إلى 3:00
    slots.append("12:00 PM")
    slots.append("12:30 PM")
    for hour in [1, 2]:
        slots.append(f"{hour:02d}:00 PM")
        slots.append(f"{hour:02d}:30 PM")
    slots.append("03:00 PM")
    return slots

DEFAULT_SLOTS = generate_default_slots()

# الأقسام الرسمية الأساسية للكلية
departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

# قاعدة البيانات الشاملة للمشروع مع ضبط الأوقات تلقائياً بين كل موعد نصف ساعة
schedule_db = {
    # --- شؤون المتدربين ورؤساء الأقسام ---
    'شؤون المتدربين': {
        'type': 'affairs',
        'dept': 'general', # متاح لجميع المتدربين بشكل عام
        'days': ['sun', 'mon', 'tue', 'wed', 'thu'],
        'slots': DEFAULT_SLOTS
    },
    'رئيس قسم الحاسب الآلي': {
        'type': 'head',
        'dept': 'computer',
        'days': ['sun', 'tue'],
        'slots': DEFAULT_SLOTS
    },
    'رئيس قسم الاتصالات': {
        'type': 'head',
        'dept': 'communications',
        'days': ['mon', 'wed'],
        'slots': DEFAULT_SLOTS
    },
    'رئيس قسم الإلكترونيات': {
        'type': 'head',
        'dept': 'electronics',
        'days': ['sun', 'tue', 'thu'],
        'slots': DEFAULT_SLOTS
    },
    'رئيس قسم المواد العامة': {
        'type': 'head',
        'dept': 'general',
        'days': ['mon', 'tue', 'wed'],
        'slots': DEFAULT_SLOTS
    },

    # --- دكاترة قسم المواد العامة ---
    'م. بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. خالد السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. خالد الزهراني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. رامي حكمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. سامر فطاني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عبدالعزيز السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله القحطاني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله البشري': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله الرفاعي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. علي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. علي الشهري': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. عمر رزق الله': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. فهيد المطيري': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. فواز الحربي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. فيصل الحارثي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. محمد ناجي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. منصور الشهراني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. هشام ابو الجدايل': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},

    # --- دكاترة ومهندسي قسم الحاسب الآلي ---
    'م. ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. احمد العمري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. أحمد رشاد': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. احمد عنقاوي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. أيمن العبيدي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. بندر الثقفي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. بندر محمد العويضي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. ثامر عطيه الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. جمعان الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. جميل الخليفي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. حسن المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. حسين احمد باداود': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. حمد الشهابي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. حامد الشيخ': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. حامد الشمراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. خالد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. خليل ال صمع': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. سالم الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. سلطان ال مغلف': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. سلمان الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. صالح الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عادل الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. عبدالرحمن المنتشري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عبدالرحمن الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله الحازمي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله السهيمي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله الشهري': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله ناصر': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عبدالهادي المالكي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عبيد الحربي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. فايز شافعي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. fهد السميري': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. محمد العرياني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. محمد الشريف': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. منصور الزهراني': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. موسى المحمادي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. وليد الغامدي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. ياسر الحبشان': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},

    # --- دكاترة ومهندسي قسم الاتصالات ---
    'م. احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'د. إيمن صائغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. بدر الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. رضا الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. سعيد ظافر': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. سامي قرامي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. سعيد عبدالرحيم': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عمر الصايغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. عيد الحربي': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عيسى السقاف': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. ماجد السريحي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. ماهر نحاس': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. محمد العلياني': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. محمد سلامي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. منصور الحازمي': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'mon'], 'slots': DEFAULT_SLOTS},
    'م. وليد جمعة': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. ياسر مياجي': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},

    # --- دكاترة ومهندسي قسم الإلكترونيات ---
    'م. اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'د. أيمن كيفي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. أيمن بنجر': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. جابر يماني': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. جميل الجهني': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. حاتم الردادي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. حاتم الزهراني': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. حسن بادويل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. حسين المكرمي': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. خالد حجازي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. رمزي مهدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. سعود المطيري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. سعود الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. سعود خوتنلي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. سعيد ابو عسيس': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. سلطان العتيبي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. صالح الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. طارق الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. ظافر الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. عبدالرحمن الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. عبدالله غرسان': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. عواض الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. فايز الشهري': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. fهد العامودي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. فوزي جلالة': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. محمد صباغ': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. محمد الرفاعي': {'type': 'faculty', 'dept': 'electronics', 'days': ['tue', 'thu'], 'slots': DEFAULT_SLOTS},
    'م. محمد عشري': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': DEFAULT_SLOTS},
    'م. هيثم نايته': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': DEFAULT_SLOTS},
    'م. يزيد الغامدي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'thu'], 'slots': DEFAULT_SLOTS}
}

@app.route('/')
def home():
    # نمرر الأقسام الأساسية + أي أقسام تمت إضافتها ديناميكياً داخل النظام لكي تظهر بالرئيسية
    return render_template('index.html', departments=departments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
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
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db)

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    dept_id = request.form.get('dept_id').strip().lower()
    dept_name = request.form.get('dept_name').strip()
    
    if dept_id and dept_name:
        if dept_id not in departments:
            # إضافة القسم في الذاكرة الحالية للعمل الفوري
            departments[dept_id] = dept_name
            head_title = f"رئيس {dept_name}"
            # إنشاء حساب رئيس القسم الجديد بجدول المواعيد الافتراضي الفارق نصف ساعة
            schedule_db[head_title] = {
                'type': 'head',
                'dept': dept_id,
                'days': ['sun', 'tue'],
                'slots': DEFAULT_SLOTS
            }
            flash(f'تم إضافة {dept_name} بنجاح وجدولته من 8 ص إلى 3 م!', 'success')
        else:
            flash('رمز القسم موجود مسبقاً!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    target_name = request.form.get('target_name')
    chosen_days = request.form.getlist('days')
    slots_input = request.form.get('slots_list')
    
    if target_name in schedule_db:
        schedule_db[target_name]['days'] = chosen_days
        schedule_db[target_name]['slots'] = [s.strip() for s in slots_input.split(',') if s.strip()]
        flash(f'تم تحديث مواعيد ({target_name}) بنجاح!', 'success')
    return redirect(url_for('admin_dashboard'))

# تم تعديل هذا المسار ليعمل مباشرة بناءً على القسم المختار دون الحاجة لتحديد نوع المسؤول أولاً
@app.route('/select_time/<dept_id>')
def select_time(dept_id):
    dept_name = departments.get(dept_id, 'القسم المحدد')
    return render_template('select_time.html', dept_id=dept_id, dept_name=dept_name, schedule_db=schedule_db)

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    
    if not target or target not in schedule_db:
        return '<span class="text-muted small">الرجاء إكمال الاختيارات أولاً.</span>'
        
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
