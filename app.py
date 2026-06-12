from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'cti_booking_secure_super_key'

# قائمة المواعيد المتاحة
AVAILABLE_SLOTS = [
    '08:00 AM - 08:30 AM', '08:30 AM - 09:00 AM', '09:00 AM - 09:30 AM',
    '09:30 AM - 10:00 AM', '10:00 AM - 10:30 AM', '10:30 AM - 11:00 AM',
    '11:00 AM - 11:30 AM', '11:30 AM - 12:00 PM', '12:00 PM - 12:30 PM'
]

# تعريف الأقسام
departments = {
    'electronics': 'قسم الإلكترونيات',
    'communications': 'قسم الاتصالات',
    'computer': 'قسم الحاسب',
    'general': 'قسم المواد العامة'
}

# قاعدة البيانات (الأسماء اللي أرسلتها)
schedule_db = {
    # قسم الإلكترونيات
    'اسماعيل فاضل': {'dept': 'electronics'}, 'أنس كرسوم': {'dept': 'electronics'},
    'أيمن كيفي': {'dept': 'electronics'}, 'أيمن بنجر': {'dept': 'electronics'},
    'جابر يماني': {'dept': 'electronics'}, 'جميل الجهني': {'dept': 'electronics'},
    'حاتم الردادي': {'dept': 'electronics'}, 'حاتم الزهراني': {'dept': 'electronics'},
    'حسن بادويل': {'dept': 'electronics'}, 'حسين المكرمي': {'dept': 'electronics'},
    'خالد حجازي': {'dept': 'electronics'}, 'رمزي مهدي': {'dept': 'electronics'},
    'سعود المطيري': {'dept': 'electronics'}, 'سعود الغامدي': {'dept': 'electronics'},
    'سعود خوتنلي': {'dept': 'electronics'}, 'سعيد ابو عسيس': {'dept': 'electronics'},
    'سلطان العتيبي': {'dept': 'electronics'}, 'صالح الشهري': {'dept': 'electronics'},
    'طارق الغامدي': {'dept': 'electronics'}, 'ظافر الشهري': {'dept': 'electronics'},
    'عبدالرحمن الغامدي': {'dept': 'electronics'}, 'عبدالله غرسان': {'dept': 'electronics'},
    'عواض الشهري': {'dept': 'electronics'}, 'فايز الشهري': {'dept': 'electronics'},
    'فهد العامودي': {'dept': 'electronics'}, 'فوزي جلالة': {'dept': 'electronics'},
    'محمد صباغ': {'dept': 'electronics'}, 'محمد الرفاعي': {'dept': 'electronics'},
    'محمد عشري': {'dept': 'electronics'}, 'هيثم نايته': {'dept': 'electronics'},
    'يزيد الغامدي': {'dept': 'electronics'},

    # قسم الاتصالات
    'احمد البار': {'dept': 'communications'}, 'امين مشدق': {'dept': 'communications'},
    'إيمن صائغ': {'dept': 'communications'}, 'بدر الجهني': {'dept': 'communications'},
    'رضا الجهني': {'dept': 'communications'}, 'سعيد ظافر': {'dept': 'communications'},
    'سامي قرامي': {'dept': 'communications'}, 'سعيد عبدالرحيم': {'dept': 'communications'},
    'عمر الصايغ': {'dept': 'communications'}, 'عيد الحربي': {'dept': 'communications'},
    'عيسى السقاف': {'dept': 'communications'}, 'ماجد السريحي': {'dept': 'communications'},
    'ماهر نحاس': {'dept': 'communications'}, 'محمد العلياني': {'dept': 'communications'},
    'محمد سلامي': {'dept': 'communications'}, 'منصور الحازمي': {'dept': 'communications'},
    'وليد جمعة': {'dept': 'communications'}, 'ياسر مياجي': {'dept': 'communications'},

    # قسم الحاسب
    'ابراهيم العديني': {'dept': 'computer'}, 'أحمد كليبي': {'dept': 'computer'},
    'احمد العمري': {'dept': 'computer'}, 'أحمد رشاد': {'dept': 'computer'},
    'احمد عنقاوي': {'dept': 'computer'}, 'أيمن العبيدي': {'dept': 'computer'},
    'بندر الثقفي': {'dept': 'computer'}, 'بندر محمد العويضي': {'dept': 'computer'},
    'ثامر عطيه الغامدي': {'dept': 'computer'}, 'جمعان الزهراني': {'dept': 'computer'},
    'جميل الخليفي': {'dept': 'computer'}, 'حسن المالكي': {'dept': 'computer'},
    'حسين احمد باداود': {'dept': 'computer'}, 'حمد الشهابي': {'dept': 'computer'},
    'حامد الشيخ': {'dept': 'computer'}, 'حامد الشمراني': {'dept': 'computer'},
    'خالد الغامدي': {'dept': 'computer'}, 'خليل ال صمع': {'dept': 'computer'},
    'سالم الزهراني': {'dept': 'computer'}, 'سلطان ال مغلف': {'dept': 'computer'},
    'سلمان الشهري': {'dept': 'computer'}, 'صالح الغامدي': {'dept': 'computer'},
    'عادل الغامدي': {'dept': 'computer'}, 'عبدالرحمن المنتشري': {'dept': 'computer'},
    'عبدالرحمن الحربي': {'dept': 'computer'}, 'عبدالله الحازمي': {'dept': 'computer'},
    'عبدالله السهيمي': {'dept': 'computer'}, 'عبدالله الشهري': {'dept': 'computer'},
    'عبدالله ناصر': {'dept': 'computer'}, 'عبدالهادي المالكي': {'dept': 'computer'},
    'عبيد الحربي': {'dept': 'computer'}, 'فايز شافعي': {'dept': 'computer'},
    'فهد السميري': {'dept': 'computer'}, 'محمد العرياني': {'dept': 'computer'},
    'محمد الشريف': {'dept': 'computer'}, 'منصور الزهراني': {'dept': 'computer'},
    'موسى المحمادي': {'dept': 'computer'}, 'وليد الغامدي': {'dept': 'computer'},
    'ياسر الحبشان': {'dept': 'computer'},

    # قسم المواد العامة
    'بندر العمودي': {'dept': 'general'}, 'تركي الغامدي': {'dept': 'general'},
    'تركي العتيبي': {'dept': 'general'}, 'خالد السلمي': {'dept': 'general'},
    'خالد الزهراني': {'dept': 'general'}, 'رامي حكمي': {'dept': 'general'},
    'سامر فطاني': {'dept': 'general'}, 'عبدالعزيز السلمي': {'dept': 'general'},
    'عبدالله القحطاني': {'dept': 'general'}, 'عبدالله البشري': {'dept': 'general'},
    'عبدالله الرفاعي': {'dept': 'general'}, 'علي الغامدي': {'dept': 'general'},
    'علي الشهري': {'dept': 'general'}, 'عمر رزق الله': {'dept': 'general'},
    'فهيد المطيري': {'dept': 'general'}, 'فواز الحربي': {'dept': 'general'},
    'فيصل الحارثي': {'dept': 'general'}, 'محمد ناجي': {'dept': 'general'},
    'منصور الشهراني': {'dept': 'general'}, 'هشام ابو الجدايل': {'dept': 'general'}
}

# المسارات
@app.route('/')
def home():
    return render_template('select_time.html', departments=departments)

# دالة الفلترة (الجديدة)
@app.route('/get_staff_by_dept', methods=['POST'])
def get_staff_by_dept():
    dept_id = request.form.get('dept_id')
    filtered_staff = {name: info for name, info in schedule_db.items() if info.get('dept') == dept_id}
    
    html = '<option value="">-- اختر الدكتور / المهندس --</option>'
    for name in filtered_staff.keys():
        html += f'<option value="{name}">{name}</option>'
    return html

if __name__ == '__main__':
    app.run(debug=True)
