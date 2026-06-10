from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'cti_booking_secret_key'

# 1. قواعد البيانات والمصفوفات الديناميكية (تفاعلية وقابلة للتعديل من لوحة الأدمن)
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

# نظام توريث الصلاحيات وإدارة حسابات الكلية بعد التخرج
admins_and_supervisors = {
    'admin_cti': 'مدير النظام العام (عمادة الكلية)',
    'affairs_user': 'مشرف شؤون المتدربين',
    'comp_head': 'رئيس قسم الحاسب الآلي'
}

# مصفوفة تخزين مواعيد الحجوزات (وهمية ومؤقتة للعرض)
booked_slots = []

# 2. مسارات واجهات المتدربين والمشرفين
@app.route('/')
def home():
    entities = {
        'affairs': 'شؤون المتدربين',
        'head': 'رئيس القسم',
        'faculty': 'أعضاء هيئة التدريس'
    }
    return render_template('index.html', entities=entities)

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
                           doctors_by_dept=doctors_by_dept)

@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    # فرز فوري للأوقات المتاحة
    slots = ['08:30 AM', '09:00 AM', '10:00 AM', '11:30 AM', '01:00 PM']
    html_output = '<div class="d-flex flex-wrap justify-content-center gap-2">'
    for slot in slots:
        html_output += f'<button type="button" class="btn btn-outline-primary slot-btn" onclick="selectSlot(\'{slot}\')">{slot}</button>'
    html_output += '</div>'
    return html_output

@app.route('/book', methods=['POST'])
def book():
    trainee_name = request.form.get('trainee_name')
    trainee_id = request.form.get('trainee_id')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    
    if not booking_time:
        flash('الرجاء اختيار الوقت المناسب من الفترات المتاحة!', 'warning')
        return redirect(request.referrer)
        
    flash(f'تم تسجيل حجزك بنجاح يا {trainee_name} بتاريخ {booking_date} الساعة {booking_time}', 'success')
    return redirect(url_for('home'))

# 3. لوحة التحكم العليا المطلقة وصلاحيات الأدمن الممتدة (Super Admin)
@app.route('/super_admin')
def super_admin():
    return render_template('admin_dashboard.html', 
                           departments=departments, 
                           doctors_by_dept=doctors_by_dept,
                           admins_and_supervisors=admins_and_supervisors)

# عمليات إدارة الأقسام بالشاشة الرئيسية
@app.route('/admin/add_department', methods=['POST'])
def add_department():
    dept_id = request.form.get('dept_id').strip().lower()
    dept_name = request.form.get('dept_name').strip()
    if dept_id and dept_name:
        departments[dept_id] = dept_name
        if dept_id not in doctors_by_dept:
            doctors_by_dept[dept_id] = []
        flash('تم إضافة القسم الجديد إلى الشاشة الرئيسية بنجاح!', 'success')
    return redirect(url_for('super_admin'))

@app.route('/admin/delete_department/<dept_id>', methods=['POST'])
def delete_department(dept_id):
    if dept_id in departments:
        del departments[dept_id]
        if dept_id in doctors_by_dept:
            del doctors_by_dept[dept_id]
        flash('تم حذف القسم وكافة الكوادر التابعة له من الواجهة!', 'danger')
    return redirect(url_for('super_admin'))

# عمليات إدارة الدكاترة والمهندسين
@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name').strip()
    if dept_id and doc_name:
        if dept_id in doctors_by_dept:
            doctors_by_dept[dept_id].append(doc_name)
            flash(f'تم تفويض وإضافة {doc_name} للقسم بنجاح!', 'success')
    return redirect(url_for('super_admin'))

@app.route('/admin/delete_doctor', methods=['POST'])
def delete_doctor():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name')
    if dept_id and doc_name in doctors_by_dept.get(dept_id, []):
        doctors_by_dept[dept_id].remove(doc_name)
        flash(f'تم سحب وإلغاء اسم {doc_name} من القائمة بنجاح!', 'danger')
    return redirect(url_for('super_admin'))

# عمليات تفويض الصلاحيات وتوريث الحسابات للكلية (بعد التخرج)
@app.route('/admin/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username').strip()
    role = request.form.get('role')
    if username and role:
        admins_and_supervisors[username] = role
        flash(f'تم تفويض حساب جديد بنجاح للمسؤول: {username} كـ ({role})', 'success')
    return redirect(url_for('super_admin'))

@app.route('/admin/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if username in admins_and_supervisors:
        del admins_and_supervisors[username]
        flash('تم إلغاء صلاحية الحساب وحذفه من النظام بنجاح!', 'danger')
    return redirect(url_for('super_admin'))

@app.route('/admin/update_slots', methods=['POST'])
def update_slots():
    flash('تم تحديث خطة عمل الأيام والفترات الزمنية فورياً بنجاح!', 'success')
    return redirect(url_for('super_admin'))

if __name__ == '__main__':
    app.run(debug=True)
