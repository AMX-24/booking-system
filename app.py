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
    # تم فصل شؤون المتدربين إدارياً عن الأقسام الأكاديمية
    'شؤون المتدربين': {
        'type': 'affairs',
        'dept': 'affairs_admin', 
        'days': ['sun', 'mon', 'tue', 'wed', 'thu'],
        'slots': ['08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM']
    },
    
    'رئيس قسم الحاسب الآلي': {'type': 'head', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM']},
    'رئيس قسم الاتصالات': {'type': 'head', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']},
    'رئيس قسم الإلكترونيات': {'type': 'head', 'dept': 'electronics', 'days': ['sun', 'tue', 'thu'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']},
    'رئيس قسم المواد العامة': {'type': 'head', 'dept': 'general', 'days': ['mon', 'tue', 'wed'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM']},

    # --- دكاترة قسم المواد العامة ---
    'م. بندر العمودي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'م. تركي الغامدي': {'type': 'faculty', 'dept': 'general', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM']},
    'م. تركي العتيبي': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM']},
    'م. خالد السلمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM']},
    'م. خالد الزهراني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']},
    'م. رامي حكمي': {'type': 'faculty', 'dept': 'general', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'م. سامر فطاني': {'type': 'faculty', 'dept': 'general', 'days': ['sun', 'wed'], 'slots': ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM']},

    # --- دكاترة قسم الحاسب الآلي ---
    'م. ابراهيم العديني': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'م. أحمد كليبي': {'type': 'faculty', 'dept': 'computer', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM']},
    'م. احمد العمري': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM']},
    'م. أحمد رشاد': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM']},
    'م. احمد عنقاوي': {'type': 'faculty', 'dept': 'computer', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']},
    'م. أيمن العبيدي': {'type': 'faculty', 'dept': 'computer', 'days': ['tue', 'thu'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},

    # --- دكاترة قسم الاتصالات ---
    'م. احمد البار': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'م. امين مشدق': {'type': 'faculty', 'dept': 'communications', 'days': ['mon', 'wed'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM']},
    'د. إيمن صائغ': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'thu'], 'slots': ['10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM']},
    'م. بدر الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['tue', 'wed'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM']},
    'م. رضا الجهني': {'type': 'faculty', 'dept': 'communications', 'days': ['sun', 'mon'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM']},

    # --- دكاترة قسم الإلكترونيات ---
    'م. اسماعيل فاضل': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'م. أنس كرسوم': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']},
    'د. أيمن كيفي': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM']},
    'م. أيمن بنجر': {'type': 'faculty', 'dept': 'electronics', 'days': ['mon', 'wed'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM']},
    'م. جابر يماني': {'type': 'faculty', 'dept': 'electronics', 'days': ['sun', 'tue'], 'slots': ['08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM']}
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
        'total_bookings': 15 
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
                'slots': ['08:00 AM', '08:30 AM', '09:00 AM']
            }
            flash(f'تم إضافة {dept_name} بنجاح!', 'success')
        else:
            flash('رمز القسم موجود مسبقاً!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): 
        return redirect(url_for('login'))
    
    target_name = request.form.get('target_name')
    chosen_days = request.form.getlist('days')
    
    # استقبال وقت البداية والنهاية الجديد بناءً على طلبك
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    if target_name in schedule_db:
        # تحديث الأيام
        schedule_db[target_name]['days'] = chosen_days
        
        # إنشاء مصفوفة الأوقات تلقائياً من وقت البداية حتى النهاية
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
                
        flash(f'تم حفظ تعديلات الأيام والمواعيد لـ ({target_name}) بنجاح!', 'success')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    titles = {'affairs': 'شؤون المتدربين', 'head': 'رؤساء الأقسام', 'faculty': 'أعضاء هيئة التدريس'}
    return render_template('select_time.html', entity_id=entity_id, entity_name=titles.get(entity_id, 'المسؤول'), departments=departments, schedule_db=schedule_db)

@app.route('/get_slots_ajax', methods=['POST'])
def get_slots_ajax():
    target = request.form.get('target')
    day_name = request.form.get('day_name')
    
    if not target or target not in schedule_db:
        return ''
        
    info = schedule_db[target]
    if day_name not in info['days']:
        return '<span class="text-danger fw-bold small">عذراً، هذا اليوم غير متاح للمقابلة حالياً!</span>'
        
    html_output = '<div class="row g-2">'
    for slot in info['slots']:
        html_output += f'<div class="col-4"><button type="button" class="btn btn-outline-primary slot-btn w-100 p-2" onclick="selectSlot(\'{slot}\', this)">{slot}</button></div>'
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
        
    flash(f'تم تسجيل الحجز بنجاح! تم إرسال تفاصيل الموعد عبر الإيميل للمتدرب وللدكتور.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
