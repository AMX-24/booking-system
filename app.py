import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
    if os.path.exists('static/logo.png'):
        return app.send_static_file('logo.png')
    else:
        return app.send_from_directory('static', 'logo.png')

@app.route('/')
def index():
    return render_template('index.html', departments=data)

@app.route('/booking/<dept_id>', methods=['GET', 'POST'])
def booking(dept_id):
    department = data.get(dept_id)
    if not department:
        return redirect(url_for('index'))

    sub_dept = request.args.get('sub_dept')

    if request.method == 'POST':
        name = request.form.get('name')
        acad_id = request.form.get('acad_id')
        selected_sub = request.form.get('sub_dept')
        time = request.form.get('time')
        
        bookings.append({
            'dept_id': dept_id,
            'sub_dept': selected_sub,
            'name': name,
            'acad_id': acad_id,
            'time': time
        })
        
        return redirect(url_for('index'))

    if str(dept_id) == '2':
        return render_template('select_time.html', department=department, dept_id=dept_id)
    return render_template('booking.html', department=department, dept_id=dept_id)

if __name__ == '__main__':
    app.run(debug=True)
