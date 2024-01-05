from server_app import app, db
from server_app.models import BenhNhan, YTa, BacSi, ThuNgan, NguoiDung, Role, PhieuDangKy
from sqlalchemy.orm.exc import NoResultFound
import hashlib

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
    
    patient = BenhNhan(nguoiDung=user, diaChi=kwargs.get('address'), soDienThoai=kwargs.get('phone'))
    db.session.add(patient)
    db.session.commit()

def register_medical(**kwargs):
    user_id = kwargs.get('user_id')
    phone = kwargs.get('phone')
    if user_id:
        benhNhan = BenhNhan.query.filter_by(id=user_id).first()
    elif phone:
        benhNhan = BenhNhan.query.filter_by(soDienThoai=phone).first()

    if benhNhan:
        phieuDK = PhieuDangKy(benhNhan_id=benhNhan.id, yTa_id=None, ngayKham=kwargs.get('date_time'))
        
        db.session.add(phieuDK)
        db.session.commit()

def count_register_medical(date):
    
    return  PhieuDangKy.query.filter_by(ngayKham=date).count()
