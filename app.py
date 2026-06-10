from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# حسابات الأدمن
ADMIN_USERS = {
    "admin_cti": "cti_password_2026",
    "affairs_user": "affairs_pass",
    "comp_head": "comp_pass"
}

# الأقسام
departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

# قاعدة البيانات الديناميكية لكل جهة/دكتور بشكل مستقل
schedule_db = {
    'شؤون المتدربين': {
        'type': 'affairs',
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
    'م. خالد الغامدي': {
        'type': 'faculty',
        'dept': 'communications',
        'days': ['mon', 'wed', 'thu'],
        'slots': ['09:00 AM', '11:30 AM']
    },
    'د. علي الشهري': {
        'type': 'faculty',
        'dept': 'computer',
        'days': ['sun', 'mon'],
        'slots': ['10:00 AM', '01:00 PM']
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
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

@app.route('/admin/update_schedule', methods=['POST'])
def update_schedule():
    if not session.get('admin_logged_in'): return redirect(url_for('login'))
    target_name = request.form.get('target_name')
    chosen_days = request.form.getlist('days')
    slots_input = request.form.get('slots_list')
    
    if target_name in schedule_db:
        schedule_db[target_name]['days'] = chosen_days
        schedule_db[target_name]['slots'] = [s.strip() for s in slots_input.split(',') if s.strip()]
        flash(f'تم تحديث مواعيد ({target_name}) فورياً ونشره للمتدربين!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- مسارات حجز المتدربين المخصصة حسب نوع الجهة ---
@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    titles = {'affairs': 'شؤون المتدربين', 'head': 'رئيس القسم', 'faculty': 'أعضاء هيئة التدريس'}
    return render_template('select_time.html', entity_id=entity_id, entity_name=titles[entity_id], departments=departments, schedule_db=schedule_db)

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
    flash('تم تسجيل حجزك بنجاح وجدولة الموعد في النظام تزامناً مع خيارات الإدارة!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
