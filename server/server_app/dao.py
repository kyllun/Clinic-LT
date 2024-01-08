from server_app import app, db
from server_app.models import *
from sqlalchemy.orm.exc import NoResultFound
import hashlib
from sqlalchemy import extract, func, not_
from io import BytesIO
from reportlab.pdfgen import canvas

def add_user(name, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = NguoiDung(hoTen=name.strip(),
                     username=username.strip(),
                     password=password,
                     loaiNguoiDung=Role.Patient)
    db.session.add(user)
    db.session.commit()

def check_login(username, password, userRole):
    if username and password and userRole: 
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())   
        # Tìm kiếm người dùng dựa trên tên đăng nhập va vai tro
        try:
            user = NguoiDung.query.filter_by(username=username.strip(), loaiNguoiDung=userRole).one()
        except NoResultFound:
            return None  # Trả về None nếu không tìm thấy người dùng
        
        # Kiểm tra mật khẩu
        if user.password == password:
            return user  # Trả về đối tượng người dùng nếu thông tin đăng nhập hợp lệ
        return None  # Trả về None nếu mật khẩu không khớp
    
def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)

def update_patient(user_id, **kwargs):
    user = NguoiDung.query.filter_by(id=user_id).first()

    if user:
        user.hoTen = kwargs.get('name')
        user.gioiTinh = kwargs.get('sex')
        user.namSinh = kwargs.get('birth')
        user.email = kwargs.get('email')
        user.avatar = kwargs.get('avatar')
    
    patient = BenhNhan(nguoiDung=user, 
                       diaChi=kwargs.get('address'), 
                       soDienThoai=kwargs.get('phone'))
    db.session.add(patient)
    db.session.commit()

def register_medical(**kwargs):
    patient_id = kwargs.get('patient_id')
    phone = kwargs.get('phone')
    nurse_id = kwargs.get('nurse_id')

    if patient_id:
        phieuDK = PhieuDangKy(benhNhan_id=patient_id,
                              yTa_id = 1,
                              ngayKham=kwargs.get('date_time'))
    elif phone:
        benhNhan = BenhNhan.query.filter_by(soDienThoai=phone).first()
        phieuDK = PhieuDangKy(benhNhan_id=benhNhan.id,
                              yTa_id=nurse_id,
                              ngayKham=kwargs.get('date_time'))
        
        db.session.add(phieuDK)
        db.session.commit()

def count_register_medical(date):
    
    return PhieuDangKy.query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date)).count()

def get_register_medical_by_date(**kwargs):
    query = db.session.query(
        NguoiDung.hoTen,
        BenhNhan.soDienThoai,
        PhieuDangKy.ngayKham,
        BenhNhan.id
    ).join(BenhNhan, PhieuDangKy.benhNhan_id.__eq__(BenhNhan.id))\
    .join(NguoiDung, BenhNhan.id.__eq__(NguoiDung.id))

    date = kwargs.get('date')
    if date:
        query = query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date))

    return query.all()

def create_medical_list_pdf(data):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Danh sách khám bệnh")
    y_coordinate = 750

    for record in data:
        pdf.drawString(100, y_coordinate, f"Họ tên: {record[0]}, Ngày giờ khám: {record[2]}, Số điện thoại: {record[1]}")
        y_coordinate -= 20  # Giả sử mỗi dòng là 20 điểm

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def count_medicine():
    return Thuoc.query.filter(Thuoc.id.isnot(None)).count()

def load_medicine(kw=None,page=1):
    drugs = Thuoc.query.filter(Thuoc.id.isnot(None))

    if kw:
        drugs = drugs.filter(Thuoc.tenThuoc.contains(kw))

    page_size =app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end =start + page_size

    return drugs.slice(start,end).all()

def count_patient():
    return BenhNhan.query.filter(BenhNhan.id.isnot(None)).count()

def load_patient(kw=None,page=1):
    query = db.session.query(
        NguoiDung.hoTen,
        PhieuKham.ngayKham,
        PhieuKham.trieuChung,
        PhieuKham.duDoan
    ).join(NguoiDung, NguoiDung.id == PhieuKham.benhNhan_id)\
    .filter(NguoiDung.loaiNguoiDung == Role.Patient)

    if kw:
        query = query.filter(NguoiDung.hoTen.contains(kw))

    page_size =app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end =start + page_size

    patients = query.slice(start, end).all()

    return patients

def add_examination_form(**kwargs):
    name = kwargs.get('name')
    date = kwargs.get('date')
    symptom = kwargs.get('symptom')
    disease = kwargs.get('disease')
    medicineName = kwargs.get('medicineName')
    quantity = kwargs.get('quantity')
    unit = kwargs.get('unit')
    id = kwargs.get('id')
    instruction = kwargs.get('instruction')

    patient = NguoiDung.query.filter_by(hoTen=name, loaiNguoiDung=Role.Patient).first()
    
    if patient:
        benhNhan_id = patient.id

    medicine = Thuoc.query.filter_by(tenThuoc=medicineName).first()
    if medicine:
        idThuoc = medicine.id

    new_examination = PhieuKham(
        ngayKham=date,
        trieuChung=symptom,
        duDoan=disease,
        benhNhan_id=benhNhan_id,
        bacSi_id = id
    )
    db.session.add(new_examination)
    db.session.commit()

    if unit:
        donvi_thuoc = DonViThuoc.query.filter_by(id=unit).first()
    
    new_prescription = ToaThuoc(
        thuoc_id=idThuoc,
        phieuKham_id=new_examination.id,
        soLuong=quantity,
        lieuLuong= donvi_thuoc.donVi,
        cachDung=instruction
    )
    db.session.add(new_prescription)
    db.session.commit()

def get_list_examination():
    try:
        medical_fees = lay_gia_tien('Tiền khám')
        subquery = db.session.query(HoaDon.phieuKham_id).subquery()
        results = db.session.query(
            NguoiDung.hoTen,
            PhieuKham.ngayKham,
            PhieuKham.id,
            medical_fees,
            Thuoc.donGia,
            ToaThuoc.soLuong,
            func.sum(Thuoc.donGia * ToaThuoc.soLuong + medical_fees)
        )\
        .join(NguoiDung, NguoiDung.id.__eq__(PhieuKham.benhNhan_id))\
        .join(ToaThuoc, ToaThuoc.phieuKham_id.__eq__(PhieuKham.id))\
        .join(Thuoc, Thuoc.id.__eq__(ToaThuoc.thuoc_id))\
        .filter(not_(PhieuKham.id.in_(subquery)))\
        .group_by(
            NguoiDung.hoTen,
            PhieuKham.ngayKham,
            PhieuKham.id,
            Thuoc.donGia,
            ToaThuoc.soLuong,
        ).all()
    except Exception as ex:
        print(ex)
    
    return results

def create_receipt(**kwargs):
    phieuKham_id = kwargs.get('phieuKham_id')
    thuNgan_id = kwargs.get('thuNgan_id')

    phieuKham_id = int(phieuKham_id)

    if thuNgan_id:
        thuNgan = NguoiDung.query.filter_by(id=thuNgan_id, loaiNguoiDung=Role.Cashier).first()
    
    if phieuKham_id:
        phieuKham = PhieuKham.query.filter_by(id=phieuKham_id).first()

    medical_fees = lay_gia_tien('Tiền khám')
    
    medicine_money = db.session.query(Thuoc.donGia)\
            .join(ToaThuoc, Thuoc.id == ToaThuoc.thuoc_id)\
            .join(PhieuKham, PhieuKham.id == ToaThuoc.phieuKham_id)\
            .filter(PhieuKham.id == phieuKham_id)\
            .first()
    
    quantity = ToaThuoc.query.filter_by(phieuKham_id=phieuKham_id).first().soLuong

    date = PhieuKham.query.filter_by(id=phieuKham_id).first().ngayKham

    total_money = medical_fees + (medicine_money[0] * quantity)

    new_receipt = HoaDon(tienKham=medical_fees,
                         tienThuoc=medicine_money[0],
                         tongTien=total_money,
                         ngayLap=date,
                         thuNgan_id=thuNgan.id,
                         phieuKham_id=phieuKham_id)
    
    db.session.add(new_receipt)
    db.session.commit()    

def lay_so_luong(name):
    medicine_amount = QuyDinh.query.filter_by(tenQuyDinh=name).first()

    if medicine_amount:
        amount = medicine_amount.moTa

        # Chuyển đổi mô tả thành số nguyên (nếu có thể)
        try:
            amount = int(amount)
            return amount
        except (TypeError, ValueError):
            return None  # Trả về None nếu không thể chuyển đổi thành số nguyên
    else:
        return None  # Trả về None nếu không tìm thấy dữ liệu phù hợp
    
def lay_gia_tien(name):
    medicine_amount = QuyDinh.query.filter_by(tenQuyDinh=name).first()

    if medicine_amount:
        amount = medicine_amount.moTa

        # Chuyển đổi mô tả thành số nguyên (nếu có thể)
        try:
            amount = float(amount)
            return amount
        except (TypeError, ValueError):
            return None  # Trả về None nếu không thể chuyển đổi thành số nguyên
    else:
        return None  # Trả về None nếu không tìm thấy dữ liệu phù hợp
    
def money_stats(month):
    with app.app_context():
        query = db.session.query(
            extract('month', HoaDon.ngayLap).label('Tháng'),
            func.sum(HoaDon.tongTien).label('Doanh thu')
        ).group_by(extract('month', HoaDon.ngayLap))

        results = query.all()

        return results
    
def tan_suat_kham(month):
    with app.app_context():
        query = db.session.query(
            extract('month', PhieuKham.ngayKham).label('Tháng'),
            (func.count(PhieuKham.id) / 30 * 100).label('Tần suất khám')
        ).group_by(extract('month', PhieuKham.ngayKham))

        if month:
            query = query.filter(extract('month', PhieuKham.ngayKham) == month)

        results = query.all()

        return results
    
def tan_suat_su_dung_thuoc(month):
    with app.app_context():
        # Tạo truy vấn cơ bản
        query = db.session.query(
            Thuoc.tenThuoc,
            extract('month', PhieuKham.ngayKham).label('Tháng'),
            (func.sum(ToaThuoc.soLuong) / 30 * 100).label('Tần suất sử dụng')
        )\
        .join(ToaThuoc, ToaThuoc.thuoc_id.__eq__(Thuoc.id))\
        .join(PhieuKham, PhieuKham.id.__eq__(ToaThuoc.phieuKham_id))\
        .group_by(Thuoc.tenThuoc, extract('month', PhieuKham.ngayKham))

        if month:
            query = query.filter(extract('month', PhieuKham.ngayKham) == month)

        results = query.all()

        return results