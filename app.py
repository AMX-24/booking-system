import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# مصفوفة البيانات المتكاملة والمطابقة للنسخة المحلية
def get_fresh_data():
    return {
        "1": {
            "name": "شؤون المتدربين",
            "slots": ["08:00 ص", "08:30 ص", "09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص"]
        },
        "2": {
            "name": "رئيس القسم",
            "slots": ["09:00 ص", "09:30 ص", "10:00 ص", "10:30 ص", "11:00 ص"]
        },
        "3": {
            "name": "عضو هيئة تدريس",
            "slots": ["08:00 ص", "08:30 ص", "09:00 ص", "09:30 ص"]
        }
    }

data = get_fresh_data()
bookings = []

@app.route('/logo.png')
def get_logo():
    logo_path = os.path.join(app.root_path, 'static', 'logo.png')
    if os.path.exists(logo_path):
        return app.send_static_file('logo.png')
    return '', 204

@app.route('/')
def index():
    return render_template('index.html', departments=data)

@app.route('/booking/<dept_id>', methods=['GET', 'POST'])
def booking(dept_id):
    department = data.get(str(dept_id))
    if not department:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '')
        acad_id = request.form.get('acad_id', '')
        sub_dept = request.form.get('sub_dept', '')
        time = request.form.get('time', '')
        
        bookings.append({
            'dept_id': str(dept_id),
            'sub_dept': sub_dept,
            'name': name,
            'acad_id': acad_id,
            'time': time
        })
        return redirect(url_for('index'))

    # استدعاء ملف select_time.html ليعمل تماماً مثل النسخة المحلية المضمونة
    return render_template('select_time.html', department=department, dept_id=dept_id)

if __name__ == '__main__':
    app.run(debug=True)
