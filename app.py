from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'cti_booking_secret_key'

# قاعدة البيانات الديناميكية (تتغير من الموقع مباشرة وتنعكس تلقائياً)
departments = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

doctors_by_dept = {
    'computer': ['م. عمار أحمد', 'د. علي الشهري'],
    'communications': ['م. خالد الغامدي', 'د. حسن الزهراني'],
    'electronics': ['م. سلطان المولد'],
    'general': ['أ. فهد القحطاني']
}

# أيام العمل والفترات الزمنية المخزنة ديناميكياً
settings = {
    'available_days': ['sun', 'mon', 'tue', 'wed', 'thu'],
    'available_slots': ['08:30 AM', '09:00 AM', '10:00 AM', '11:30 AM']
}

@app.route('/')
def home():
    # نتحقق إذا كان المستخدم داخل بوضع الأدمن عبر الـ URL (مثال: /?mode=admin)
    admin_mode = request.args.get('mode') == 'admin'
    
    entities = {
        'affairs': 'شؤون المتدربين',
        'head': 'رئيس القسم',
        'faculty': 'أعضاء هيئة التدريس'
    }
    return render_template('index.html', 
                           entities=entities, 
                           admin_mode=admin_mode, 
                           departments=departments, 
                           doctors_by_dept=doctors_by_dept,
                           settings=settings)

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    entities = {
        'affairs': 'شؤون المتدربين',
        'head': 'رئيس القسم',
        'faculty': 'أعضاء هيئة التدريس'
    }
    entity_name = entities.get(entity_id, 'الجهة المطلوبة')
    return render_template('select_time.html', 
                           entity_id=entity_id, 
                           entity_name=entity_name, 
                           departments=departments, 
                           doctors_by_dept=doctors_by_dept,
                           settings=settings)

@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    # الفرز يعتمد على فترات الوقت المحدثة من قبل الأدمن تلقائياً
    html_output = '<div class="d-flex flex-wrap justify-content-center gap-2">'
    for slot in settings['available_slots']:
        html_output += f'<button type="button" class="btn btn-outline-primary slot-btn" onclick="selectSlot(\'{slot}\')">{slot}</button>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    trainee_name = request.form.get('trainee_name')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    
    if not booking_time:
        flash('الرجاء اختيار الوقت المناسب من الفترات المتاحة!', 'warning')
        return redirect(request.referrer)
        
    flash(f'تم تسجيل حجزك بنجاح يا {trainee_name} بتاريخ {booking_date} الساعة {booking_time}', 'success')
    return redirect(url_for('home'))

# --- مسارات التعديل الفوري من الموقع للأدمن ---

@app.route('/admin/add_dept', methods=['POST'])
def add_dept():
    dept_id = request.form.get('dept_id').strip().lower()
    dept_name = request.form.get('dept_name').strip()
    if dept_id and dept_name:
        departments[dept_id] = dept_name
        if dept_id not in doctors_by_dept:
            doctors_by_dept[dept_id] = []
        flash('تم إضافة القسم الجديد بنجاح في النظام تزامناً مع الطلاب!', 'success')
    return redirect(url_for('home', mode='admin'))

@app.route('/admin/delete_dept/<dept_id>', methods=['POST'])
def delete_dept(dept_id):
    if dept_id in departments:
        del departments[dept_id]
        if dept_id in doctors_by_dept:
            del doctors_by_dept[dept_id]
        flash('تم حذف القسم وكافة الكوادر التابعة له فورياً!', 'danger')
    return redirect(url_for('home', mode='admin'))

@app.route('/admin/add_doc', methods=['POST'])
def add_doc():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name').strip()
    if dept_id and doc_name:
        if dept_id in doctors_by_dept:
            doctors_by_dept[dept_id].append(doc_name)
            flash(f'تم إضافة {doc_name} إلى القائمة بنجاح!', 'success')
    return redirect(url_for('home', mode='admin'))

@app.route('/admin/delete_doc', methods=['POST'])
def delete_doc():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name')
    if dept_id and doc_name in doctors_by_dept.get(dept_id, []):
        doctors_by_dept[dept_id].remove(doc_name)
        flash(f'تم حذف {doc_name} من القائمة بنجاح!', 'danger')
    return redirect(url_for('home', mode='admin'))

@app.route('/admin/update_system_settings', methods=['POST'])
def update_system_settings():
    # تحديث الأيام النشطة
    chosen_days = request.form.getlist('days')
    settings['available_days'] = chosen_days
    
    # تحديث فترات الساعات المتاحة من المدخلات
    slots_input = request.form.get('slots_list')
    if slots_input:
        # فصل الساعات المكتوبة بالفواصل وتحويلها لمصفوفة
        settings['available_slots'] = [s.strip() for s in slots_input.split(',') if s.strip()]
        
    flash('تم تحديث أوقات العمل والأيام المتاحة، وتغيرت تلقائياً عند المتدربين!', 'success')
    return redirect(url_for('home', mode='admin'))

if __name__ == '__main__':
    app.run(debug=True)
