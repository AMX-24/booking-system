import os
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

# مصفوفة البيانات الثابتة للأقسام والمواعيد
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

bookings = []

# صفحة الواجهة الرئيسية المدمجة (بديلة لملف index.html المفقود)
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>بوابة حجز المواعيد</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f6f4; text-align: center; padding-top: 50px; }
        .container { background: white; padding: 40px; border-radius: 15px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #1e4620; }
        .btn-dept { display: block; background-color: #2e7d32; color: white; padding: 15px; margin: 15px 0; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 18px; transition: 0.2s; }
        .btn-dept:hover { background-color: #153317; }
    </style>
</head>
<body>
    <div class="container">
        <h1>بوابة حجز المواعيد الإلكترونية</h1>
        <p>الرجاء اختيار الجهة المطلوبة لاستكمال الحجز:</p>
        {% for id, dept in departments.items() %}
            <a href="/booking/{{ id }}" class="btn-dept">{{ dept.name }}</a>
        {% endfor %}
    </div>
</body>
</html>
"""

# صفحة استكمال البيانات الذكية المدمجة بدون ملفات خارجية تالفة
BOOKING_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>استكمال بيانات الحجز</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f6f4; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px 0; }
        .booking-card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); width: 100%; max-width: 480px; }
        h2 { text-align: center; color: #333; margin-top: 0; }
        .dept-title { background-color: #f0f0f0; padding: 10px; text-align: center; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
        .slots-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }
        .slot-option { border: 1px solid #2e7d32; padding: 10px; border-radius: 8px; text-align: center; background-color: #e8f5e9; cursor: pointer; font-size: 14px; }
        .slot-option input { display: none; }
        .slot-option:has(input:checked) { background-color: #a5d6a7; border-color: #1b5e20; font-weight: bold; }
        .btn-submit { background-color: #1e4620; color: white; width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; margin-top: 20px; cursor: pointer; }
        .btn-cancel { display: block; text-align: center; margin-top: 15px; color: #666; text-decoration: none; font-size: 14px; }
    </style>
</head>
<body>
<div class="booking-card">
    <h2>استكمال بيانات الحجز</h2>
    <div class="dept-title">الجهة: {{ department.name }}</div>

    <form method="POST" action="/booking/{{ dept_id }}">
        <div class="form-group">
            <label>اسم المتدرب / الثلاثي:</label>
            <input type="text" name="name" class="form-control" required placeholder="أدخل اسمك الثلاثي">
        </div>
        
        <div class="form-group">
            <label>الرقم الأكاديمي:</label>
            <input type="text" name="acad_id" class="form-control" required placeholder="أدخل الرقم الأكاديمي">
        </div>

        {% if dept_id == '2' %}
        <div class="form-group">
            <label>تحديد القسم المختص:</label>
            <select name="sub_dept" class="form-control" required>
                <option value="">-- اختر رئيس القسم --</option>
                <option value="رئيس قسم الحاسب">رئيس قسم الحاسب</option>
                <option value="رئيس قسم الاتصالات">رئيس قسم الاتصالات</option>
                <option value="رئيس قسم الإلكترونيات">رئيس قسم الإلكترونيات</option>
                <option value="رئيس قسم المواد العامة">رئيس قسم المواد العامة</option>
            </select>
        </div>
        {% endif %}

        {% if dept_id == '3' %}
        <div class="form-group">
            <label>اختر القسم المختص:</label>
            <select id="faculty-dept" name="sub_dept" class="form-control" required onchange="updateDoctors()">
                <option value="">-- اختر القسم --</option>
                <option value="قسم الحاسب">قسم الحاسب</option>
                <option value="قسم الاتصالات">قسم الاتصالات</option>
                <option value="قسم الإلكترونيات">قسم الإلكترونيات</option>
                <option value="قسم المواد العامة">قسم المواد العامة</option>
            </select>
        </div>

        <div class="form-group">
            <label>اختر اسم الدكتور / المدرب:</label>
            <select id="doctor-select" name="doctor_name" class="form-control" required>
                <option value="">-- يرجى اختيار القسم أولاً --</option>
            </select>
        </div>
        {% endif %}

        <div class="form-group">
            <label>اختر الوقت المناسب:</label>
            <div class="slots-grid">
                {% for slot in department.slots %}
                    <label class="slot-option">
                        <input type="radio" name="time" value="{{ slot }}" required>
                        <span>{{ slot }}</span>
                    </label>
                {% endfor %}
            </div>
        </div>

        <button type="submit" class="btn-submit">تأكيد الحجز</button>
        <a href="/" class="btn-cancel">إلغاء والعودة للرئيسية</a>
    </form>
</div>

<script>
function updateDoctors() {
    const deptSelect = document.getElementById('faculty-dept');
    const docSelect = document.getElementById('doctor-select');
    const selectedDept = deptSelect.value;
    
    docSelect.innerHTML = '<option value="">-- اختر اسم الدكتور --</option>';
    
    const doctors = {
        "قسم الحاسب": [
            "ابراهيم العديني", "أحمد كليبي", "احمد العمري", "أحمد رشاد", 
            "احمد عنقاوي", "أيمن العبيدي", "بندر الثقفي", "بندر محمد العويضي", 
            "ثامر عطيه الغامدي", "جمعان الزهراني", "جميل الخليفي", "حسن المالكي", 
            "حسين احمد باداود", "حمد الشهابي", "حامد الشيخ", "حامد الشمراني", 
            "خالد الغامدي", "خليل ال صمع", "سالم الزهراني", "سلطان ال مغلف", 
            "سلمان الشهري", "صالح الغامدي", "عادل الغامدي", "عبدالرحمن المنتشري", 
            "عبدالرحمن الحربي", "عبدالله الحازمي", "عبدالله السهيمي", "عبدالله الشهري", 
            "عبدالله ناصر", "عبدالهادي المالكي", "عبيد الحربي", "فايز شافعي", 
            "فهد السميري", "محمد العرياني", "محمد الشريف", "منصور الزهراني", 
            "موسى المحمادي", "وليد الغامدي", "ياسر الحبشان"
        ],
        "قسم الاتصالات": [
            "احمد البار", "امين مشدق", "إيمن صائغ", "بدر الجهني", 
            "رضا الجهني", "سعيد ظافر", "سامي قرامي", "سعيد عبدالرحيم", 
            "عمر الصايغ", "عيد الحربي", "عيسى السقاف", "ماجد السريحي", 
            "ماهر نحاس", "محمد العلياني", "محمد سلامي", "منصور الحازمي", 
            "وليد جمعة", "ياسر مياجي"
        ],
        "قسم الإلكترونيات": [
            "اسماعيل فاضل", "أنس كرسوم", "أيمن كيفي", "أيمن بنجر", 
            "جابر يماني", "جميل الجهني", "حاتم الردادي", "حاتم الزهراني", 
            "حسن بادويل", "حسين المكرمي", "خالد حجازي", "رمزي مهدي", 
            "سعود المطيري", "سعود الغامدي", "سعود خوتنلي", "سعيد ابو عسيس", 
            "سلطان العتيبي", "صالح الشهري", "طارق الغامدي", "ظافر الشهري", 
            "عبدالرحمن الغامدي", "عبدالله غرسان", "عواض الشهري", "فايز الشهري", 
            "فهد العامودي", "فوزي جلالة", "محمد صباغ", "محمد الرفاعي", 
            "محمد عشري", "هيثم نايته", "يزيد الغامدي"
        ],
        "قسم المواد العامة": [
            "بندر العمودي", "تركي الغامدي", "تركي العتيبي", "خالد السلمي", 
            "خالد الزهراني", "رامي حكمي", "سامر فطاني", "عبدالعزيز السلمي", 
            "عبدالله القحطاني", "عبدالله البشري", "عبدالله الرفاعي", "علي الغامدي", 
            "علي الشهري", "عمر رزق الله", "فهيد المطيري", "فواز الحربي", 
            "فيصل الحارثي", "محمد ناجي", "منصور الشهراني", "هشام ابو الجدايل"
        ]
    };
    
    if (selectedDept && doctors[selectedDept]) {
        doctors[selectedDept].forEach(function(docName) {
            const option = document.createElement('option');
            option.value = docName;
            option.text = docName;
            docSelect.appendChild(option);
        });
    }
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, departments=DEPARTMENTS_DATA)

@app.route('/booking/<dept_id>', methods=['GET', 'POST'])
def booking(dept_id):
    department = DEPARTMENTS_DATA.get(str(dept_id))
    if not department:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '')
        acad_id = request.form.get('acad_id', '')
        sub_dept = request.form.get('sub_dept', '')
        doctor_name = request.form.get('doctor_name', '')
        time = request.form.get('time', '')
        
        bookings.append({
            'dept_id': str(dept_id),
            'sub_dept': sub_dept,
            'doctor_name': doctor_name,
            'name': name,
            'acad_id': acad_id,
            'time': time
        })
        return redirect(url_for('index'))

    return render_template_string(BOOKING_TEMPLATE, department=department, dept_id=dept_id)

if __name__ == '__main__':
    app.run(debug=True)
