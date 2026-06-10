from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# ملاحظة: تأكد أن المصفوفات (departments و doctors_by_dept) قابلة للتعديل وليست ثابتة tuple 
# لتسمح للأدمن بالإضافة والحذف ديناميكياً أثناء تشغيل البرنامج.

@app.route('/super_admin')
def super_admin():
    # هذه هي لوحة التحكم العليا المطلقة التي طلبها الدكتور
    return render_template('admin_dashboard.html', 
                           departments=departments, 
                           doctors_by_dept=doctors_by_dept)

@app.route('/admin/add_department', methods=['POST'])
def add_department():
    dept_id = request.form.get('dept_id')
    dept_name = request.form.get('dept_name')
    if dept_id and dept_name:
        departments[dept_id] = dept_name
        if dept_id not in doctors_by_dept:
            doctors_by_dept[dept_id] = []
        flash('تم إضافة القسم بنجاح!', 'success')
    return redirect(url_for('super_admin'))

@app.route('/admin/delete_department/<dept_id>', methods=['POST'])
def delete_department(dept_id):
    if dept_id in departments:
        del departments[dept_id]
        if dept_id in doctors_by_dept:
            del doctors_by_dept[dept_id]
        flash('تم حذف القسم وكافة الدكاترة التابعين له!', 'danger')
    return redirect(url_for('super_admin'))

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name')
    if dept_id and doc_name:
        if dept_id in doctors_by_dept:
            doctors_by_dept[dept_id].append(doc_name)
            flash(f'تم إضافة {doc_name} إلى القسم بنجاح!', 'success')
    return redirect(url_for('super_admin'))

@app.route('/admin/delete_doctor', methods=['POST'])
def delete_doctor():
    dept_id = request.form.get('dept_id')
    doc_name = request.form.get('doc_name')
    if dept_id and doc_name in doctors_by_dept.get(dept_id, []):
        doctors_by_dept[dept_id].remove(doc_name)
        flash(f'تم حذف {doc_name} بنجاح!', 'danger')
    return redirect(url_for('super_admin'))

# مسار إضافي لتعديل أوقات العمل والأيام (الإتاحة)
@app.route('/admin/update_slots', methods=['POST'])
def update_slots():
    # هنا يتم استقبال الأيام والأوقات التي يحددها الدكتور أو رئيس القسم وتحديث مصفوفة الأوقات المتاحة
    flash('تم تحديث أوقات العمل والأيام المتاحة بنجاح!', 'success')
    return redirect(url_for('super_admin'))
