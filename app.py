import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DEPARTMENTS_DATA = {
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

confirmed_bookings = []

@app.route('/logo.png')
def get_logo():
    logo_path = os.path.join(app.root_path, 'static', 'logo.png')
    if os.path.exists(logo_path):
        return app.send_static_file('logo.png')
    return '', 204

@app.route('/')
def index():
    return render_template('index.html', departments=DEPARTMENTS_DATA)

@app.route('/booking/<dept_id>', methods=['GET', 'POST'])
def booking(dept_id):
    department = DEPARTMENTS_DATA.get(str(dept_id))
    if not department:
        return redirect(url_for('index'))

    booked_slots = [b['time'] for b in confirmed_bookings if b['dept_id'] == str(dept_id)]

    available_slots = [slot for slot in department['slots'] if slot not in booked_slots]

    if request.method == 'POST':
        name = request.form.get('name', '')
        acad_id = request.form.get('acad_id', '')
        selected_time = request.form.get('time', '')

        if selected_time and selected_time not in booked_slots:
            confirmed_bookings.append({
                'dept_id': str(dept_id),
                'name': name,
                'acad_id': acad_id,
                'time': selected_time
            })
        
        return redirect(url_for('index'))

    return render_template('booking.html', department=department, dept_id=dept_id, slots=available_slots)

if __name__ == '__main__':
    app.run(debug=True)
