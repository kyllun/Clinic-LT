from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from __init__ import db, app
from datetime import datetime
from flask_login import UserMixin
from enum import Enum as UserEnum

class Role(UserEnum):
    Admin = 1
    Nurse = 2
    Doctor = 3
    Cashier = 4
    Patient = 5

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

class TaiKhoan(BaseModel, UserMixin):
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))

    def __str__(self):
        return self.name

class NguoiDung(BaseModel):
    __abstract__ = True
    hoTen = Column(String(50), nullable=False)
    gioiTinh = Column(Boolean)
    namSinh = Column(DateTime)
    loaiTaiKhoan = Column(Enum(Role))

class BenhNhan(NguoiDung):
    __tablename__ = 'benh_nhan'
    diaChi = Column(String(100))
    hoSoBenhNhan = relationship('HoSoBenhNhan', uselist=False, back_populates='benhNhan')
    danhSachKham = relationship('PhieuDangKy', backref='benhNhan', lazy=True)

    def __str__(self):
        return self.name
    
class YTa(NguoiDung):
    __tablename__ = 'y_ta'
    phuTrach = Column(String(100))
    danhSachKham = relationship('DanhSachKham', backref='yTa', lazy=True)
    hoSoBenhNhan = relationship('HoSoBenhNhan', backref='yTa', lazy=True)

    def __str__(self):
        return self.name
    
class BacSi(NguoiDung):
    __tablename__ = 'bac_si'
    chuyenMon = Column(String(50))

    def __str__(self):
        return self.name
    
class ThuNgan(NguoiDung):
    __tablename__ = 'thu_ngan'
    trinhDo = Column(String(50))

    def __str__(self):
        return self.name
    
class DanhSachKham(BaseModel):
    __tablename__ = 'danh_sach_kham'
    soLuongBenhNhan = Column(Integer, nullable=False)
    yTa_id = Column(Integer, ForeignKey('y_ta.id'), nullable=False)
    benhNhan = relationship('PhieuDangKy', backref='danhSachKham', lazy=True)

    def __str__(self):
        return self.name
    
class PhieuDangKy(BaseModel):
    __tablename__ = 'phieu_dang_ky'
    ngayKham = Column(DateTime, nullable=False)
    danhSachKham_id = Column(Integer, ForeignKey('danh_sach_kham.id'), nullable=False)
    benhNhan_id = Column(Integer, ForeignKey('benh_nhan.id'), nullable=False)

    def __str__(self):
        return self.name
    
class HoSoBenhNhan(BaseModel):
    __tablename__ = 'ho_so_benh_nhan'
    lichSuBenh = Column(String(100))
    benhNhan_id = Column(Integer, ForeignKey('benh_nhan.id'), unique=True)
    benhNhan = relationship('BenhNhan', back_populates='hoSoBenhNhan')
    yTa_id = Column(Integer, ForeignKey('y_ta.id'), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()