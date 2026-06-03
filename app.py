from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__, template_folder='.')

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
        
        if selected_sub and "sub_sections" in department:
            if time in department["sub_sections"][selected_sub]:
                department["sub_sections"][selected_sub].remove(time)
        elif time in department.get("slots", []):
            department["slots"].remove(time)
            
        bookings.append({
            "name": name, 
            "id": acad_id, 
            "section": department["name"], 
            "sub_section": selected_sub, 
            "time": time
        })
        return render_template('success.html')
        
    return render_template('booking.html', dept_id=dept_id, department=department, sub_dept=sub_dept)

@app.route('/admin')
def admin_panel():
    return render_template('admin.html', bookings=bookings)

@app.route('/clear')
def clear_data():
    bookings.clear()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
