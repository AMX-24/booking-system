from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# قاعدة البيانات: كل قسم أو رئيس قسم له قائمة مواعيد مستقلة
data = {
    "1": {
        "name": "شؤون المتدربين",
        "slots": ["08:00 ص", "08:30 ص", "09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص"]
    },
    "2": {
        "name": "رئيس القسم",
        "sub_sections": {
            "رئيس قسم الحاسب": ["09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص", "11:00 ص"],
            "رئيس قسم الاتصالات": ["09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص", "11:00 ص"],
            "رئيس قسم الإلكترونيات": ["09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص", "11:00 ص"],
            "رئيس قسم المواد العامة": ["09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص", "11:00 ص"]
        }
    },
    "3": {
        "name": "عضو هيئة تدريس",
        "slots": ["08:00 ص", "08:30 ص", "09:00 ص", "09:30 ص"]
    }
}

bookings = []

@app.route('/')
def index():
    return render_template('index.html', departments=data)

@app.route('/select_time/<dept_id>')
def select_time(dept_id):
    dept = data.get(dept_id)
    if dept:
        return render_template('select_time.html', dept_id=dept_id, dept=dept)
    return redirect(url_for('index'))

@app.route('/reserve/<dept_id>', methods=['POST'])
def reserve(dept_id):
    name = request.form.get('student_name')
    acad_id = request.form.get('academic_id')
    time = request.form.get('selected_time')
    manager_name = request.form.get('manager_name')
    
    if dept_id in data:
        target_dept = data[dept_id]
        section_display = manager_name if manager_name else target_dept['name']

        # حذف الوقت المختار لكي لا يظهر لمتدرب آخر
        if manager_name and "sub_sections" in target_dept:
            if time in target_dept["sub_sections"][manager_name]:
                target_dept["sub_sections"][manager_name].remove(time)
        elif "slots" in target_dept:
            if time in target_dept["slots"]:
                target_dept["slots"].remove(time)

        bookings.append({
            "name": name, "id": acad_id, "section": section_display, "time": time
        })
        return render_template('success.html', name=name, time=time, section=section_display)
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    return render_template('admin.html', bookings=bookings)

@app.route('/clear')
def clear_data():
    bookings.clear()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0' , port=port)
