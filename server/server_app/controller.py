from flask import render_template, url_for, redirect, request, session, jsonify, send_file
from server_app import app, db, dao, login, utils, admin, client, verify_sid
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role
from datetime import datetime
import cloudinary
import cloudinary.uploader
import math

@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        try:
            if(password.strip().__eq__(confirm.strip())):
                dao.add_user(name=name, 
                             username=username, 
                             password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi' +str(ex)

    return render_template("register_page.html", 
                           err_msg=err_msg)

@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        userRole = request.form.get('userRole')

        user = dao.check_login(username=username, 
                               password=password, 
                               userRole=userRole)

        if user:
            login_user(user=user) #current_user

            return redirect(url_for('home_page'))
        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template("login_page.html", 
                           err_msg=err_msg)

@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_login'))

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.context_processor
def common_responses():
    return {
        'medicine_state': utils.counter_medicine(session.get('medicine')),
        'Role': Role
    }

@app.route("/patient_information")
def patient_information():    
    return render_template("patient_infomation_page.html")

@app.route("/patient_information/<int:user_id>", methods=['get', 'post'])
def update_patient_infor(user_id):
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        sex = request.form.get('sex')
        birth = request.form.get('birth')
        email = request.form.get('email')
        avatar = request.files.get('avatar')
        avatar_path = None
        if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
        address = request.form.get('address')
        phone = request.form.get('phone')

        dao.update_patient(user_id=user_id, 
                           name=name, 
                           sex=sex, 
                           birth=birth, 
                           email=email, 
                           avatar=avatar_path, 
                           address=address, 
                           phone=phone)
        return redirect(url_for('home_page'))

@app.route('/register_medical', methods=['get', 'post'])
def medical_register():
    msg = ''
    if not current_user.is_authenticated:
        return redirect('/login')
    elif current_user.loaiNguoiDung == Role.Patient: 
        if request.method.__eq__('POST'):
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
            count = dao.count_register_medical(date = date)
            quyDinh = dao.lay_so_luong('Số lượng khám')
            
            if count > 0 and count < quyDinh:
                dao.register_medical(patient_id=current_user.id, 
                                     date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'

            if not msg:
                return redirect(url_for('home_page'))
            
    elif current_user.loaiNguoiDung == Role.Nurse: 
        if request.method.__eq__('POST'):
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')           
            count = dao.count_register_medical(date = date)
            quyDinh = dao.lay_so_luong('Số lượng khám')

            if count > 0 and count < quyDinh:
                dao.register_medical(phone=phone, 
                                     date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'
            
            if not msg:
                return redirect(url_for('home_page'))
    return render_template('medical_register_page.html', 
                           msg=msg)
    
@app.route("/medical_list", methods=['get'])
def medical_list():
    date = request.args.get('date')
    medical_list = dao.get_register_medical_by_date(date=date)

    return render_template('medical_examination_list_page.html', 
                           medical_list=medical_list)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    date = request.args.get('date')
    medical_list = dao.get_register_medical_by_date(date=date)
    pdf = dao.create_medical_list_pdf(medical_list)
    pdf.seek(0)  # Đảm bảo con trỏ ở đầu tệp

    return send_file(
        pdf,
        attachment_filename='medical_list.pdf',
        as_attachment=True,
        mimetype='application/pdf'  # Thiết lập mimetype cho header
    )

@app.route("/medicine")
def drugs_list():
    kw = request.args.get("keywordthuoc")
    counter = dao.count_medicine()
    page = request.args.get("page", 1)
    drugs = dao.load_medicine(kw=kw, page=int(page))
    return render_template('medicine.html',
                           drugs=drugs,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route('/login_admin',methods=['post', 'get'])
def login_admin():
    if request.method.__eq__('POST'):
        username = request.form.get('usernameAd')
        password = request.form.get('passwordAd')

        user = dao.check_login(username=username, 
                               password=password,
                               userRole=Role.Admin)

        if user:
            login_user(user=user)

    return redirect('/admin')

#===========================================================
@app.route('/examination_form', methods=['get', 'post'])
def create_examination_form():
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        date = request.form.get('date')
        symptom = request.form.get('symptom')
        disease = request.form.get('disease')
        medicineName = request.form.get('medicineName')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        instruction = request.form.get('instruction')

        # try:
        #     name = dao.check_name_patient(name=name)
        # except:
        #     msg ='khong tim thay benh nhan'
        # else:
        dao.add_examination_form(name=name,
                                date=date,
                                symptom=symptom,
                                disease=disease,
                                medicineName=medicineName,
                                quantity=quantity,
                                unit=unit,
                                instruction=instruction,
                                id=current_user.id)

    return render_template('examination_form.html')

@app.route("/patient_search")
def patient_list():
    kw = request.args.get("keywordPatient")
    counter = dao.count_patient()
    page = request.args.get("page", 1)
    patients = dao.load_patient(kw=kw, page=int(page))
    return render_template('search_patient.html',
                           patients=patients,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route('/api/save_exam_data', methods=['POST'])
def save_exam_data():
    data = request.json 
    session['exam_data'] = data  
    return jsonify({'message': 'Exam data saved successfully'})

@app.route('/api/get_exam_data', methods=['GET'])
def get_exam_data():
    exam_data = session.get('exam_data', {})
    print(exam_data)
    return jsonify(exam_data)

@app.route('/receipt', methods=['GET', 'post'])
def receipt():
    list_examination = dao.get_list_examination()

    return render_template('receipt.html', 
                           list_examination=list_examination)

@app.route('/api/pay', methods=['post'])
def pay():
    data = request.json
    id = str(data.get('phieuKhamId'))

    try:
        dao.create_receipt(phieuKham_id=id,
                       thuNgan_id=current_user.id)
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})
   
if __name__ == '__main__':
    app.run(debug=True)