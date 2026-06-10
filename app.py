from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# حسابات الأدمن لتسجيل الدخول الآمن
ADMIN_USERS = {
    "admin_cti": "cti_password_2026",
    "affairs_user": "affairs_pass",
    "comp_head": "comp_pass"
}

# الأقسام الافتراضية للمشروع
departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

# قاعدة بيانات ديناميكية لكل دكتور أو رئيس قسم (تشمل أيامه وساعاته الخاصة)
# يمكن للأدمن تعديلها بالكامل من الموقع وتتغير عند المتدرب افتراضياً
schedule_db = {
    'م. عمار أحمد': {
        'dept': 'computer',
        'days': ['sun', 'tue'],
        'slots': ['08:30 AM', '10:00 AM']
    },
    'م. خالد الغامدي': {
        'dept': 'communications',
        'days': ['mon', 'wed', 'thu'],
        'slots': ['09:00 AM', '11:30 AM', '01:00 PM']
    },
    'د. علي الشهري': {
        'dept': 'computer',
        'days': ['sun', 'mon', 'wed'],
        'slots': ['10:00 AM', '11:00 AM']
    },
    'شؤون المتدربين': {
        'dept': 'general',
        'days': ['sun', 'mon', 'tue', 'wed', 'thu'],
        'slots': ['08:00 AM', '09:30 AM', '11:00 AM']
    }
}

@app.route('/')
def home():
    entities = {
        'affairs': 'شؤون المتدربين',
        'head': 'رئيس القسم',
        'faculty': 'أعضاء هيئة التدريس'
    }
    return render_template('index.html', entities=entities)

# --- صفحة تسجيل الدخول الآمنة للأدمن ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('تم تسجيل الدخول بنجاح إلى لوحة التحكم العليا المطلقة!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('home'))

# --- لوحة تحكم الأدمن المستقلة (نفس ستايل الصورة الثانية) ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('عذراً، يجب تسجيل الدخول أولاً للوصول لهذه الصفحة!', 'danger')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', departments=departments, schedule_db=schedule_db)

# مسار تعديل أوقات وأيام دكتور أو رئيس قسم محدد بحد ذاته
@app.route('/admin/update_doctor_schedule', methods=['POST'])
def update_doctor_schedule():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    
    doc_name = request.form.get('doc_name')
    chosen_days = request.form.getlist('days')
    slots_input = request.form.get('slots_list')
    
    if doc_name in schedule_db:
        schedule_db[doc_name]['days'] = chosen_days
        schedule_db[doc_name]['slots'] = [s.strip() for s in slots_input.split(',') if s.strip()]
        flash(f'تم تحديث مواعيد وأيام ({doc_name}) بنجاح وتغيرت تلقائياً عند المتدربين!', 'success')
    return redirect(url_for('admin_dashboard'))

# مسار إضافة دكتور/رئيس قسم جديد مع تحديد قسمه
@app.route('/admin/add_new_doctor', methods=['POST'])
def add_new_doctor():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    
    doc_name = request.form.get('doc_name').strip()
    dept_id = request.form.get('dept_id')
    
    if doc_name and doc_name not in schedule_db:
        schedule_db[doc_name] = {
            'dept': dept_id,
            'days': ['sun', 'mon', 'tue', 'wed', 'thu'],
            'slots': ['08:30 AM', '10:00 AM']
        }
        flash(f'تم إضافة {doc_name} إلى النظام بنجاح، يمكنك الآن تخصيص وقته.', 'success')
    return redirect(url_for('admin_dashboard'))

# مسار حذف دكتور/رئيس قسم من النظام
@app.route('/admin/delete_doctor/<doc_name>', methods=['POST'])
def delete_doctor(doc_name):
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    
    if doc_name in schedule_db:
        del schedule_db[doc_name]
        flash(f'تم حذف {doc_name} من النظام نهائياً.', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- مسارات المتدربين (قراءة الساعات الخاصة بكل دكتور) ---
@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    entities = {'affairs': 'شؤون المتدربين', 'head': 'رئيس القسم', 'faculty': 'أعضاء هيئة التدريس'}
    entity_name = entities.get(entity_id, 'الجهة المطلوبة')
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=departments, schedule_db=schedule_db)

@app.route('/get_doctor_slots', methods=['POST'])
def get_doctor_slots():
    doc_name = request.form.get('doctor')
    date_input = request.form.get('date')
    
    if not doc_name or not date_input or doc_name not in schedule_db:
        return '<span class="text-muted small">الرجاء اختيار الدكتور والتاريخ لاستعراض الساعات.</span>'
        
    day_name = new_date = request.form.get('day_name').lower() # يرسل عبر الجافاسكربت
    doc_info = schedule_db[doc_name]
    
    # التحقق من أن اليوم متاح لهذا الدكتور بحد ذاته
    if day_name not in doc_info['days']:
        return '<span class="text-danger fw-bold small">عذراً، هذا اليوم غير متاح للمقابلة مع هذا الدكتور حالياً!</span>'
        
    # توليد أزرار الساعات الخاصة بالدكتور المختار
    html_output = '<div class="d-flex flex-wrap justify-content-center gap-2">'
    for slot in doc_info['slots']:
        html_output += f'<button type="button" class="btn btn-outline-primary slot-btn btn-sm" onclick="selectSlot(\'{slot}\')">{slot}</button>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    trainee_name = request.form.get('trainee_name')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    doctor = request.form.get('doctor')
    
    if not booking_time:
        flash('الرجاء اختيار الوقت المناسب من الفترات المتاحة للدكتور!', 'warning')
        return redirect(request.referrer)
        
    flash(f'تم تسجيل حجزك بنجاح مع ({doctor}) بتاريخ {booking_date} الساعة {booking_time}', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
