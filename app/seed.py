"""Nap du lieu mau khi database con rong.

Chi chay khi TAO_DU_LIEU_MAU=true. Tren production that thi dat false.

Du lieu co y de "nhu that": 18 dau sach, 10 doc gia, va mot it lich su muon tra —
du nhieu de /thong-ke va /thong-ke/sach-muon-nhieu ra so co nghia ngay lan dau mo.
"""
from datetime import date, timedelta

from app.auth import bam_mat_khau
from app.config import cau_hinh
from app.database import SessionLocal
from app.models import DocGia, NguoiDung, PhieuMuon, Sach

TAI_KHOAN = [
    ("thuthu", "thuthu123", True),
    ("khach", "khach123", False),
]

SACH_MAU = [
    ("9786041234567", "Doi Mua Bui", "Duyen Anh", 1992, 3),
    ("9786041234574", "So Do", "Vu Trong Phung", 1936, 2),
    ("9786041234581", "De Men Phieu Luu Ky", "To Hoai", 1941, 5),
    ("9786041234598", "Mat Biec", "Nguyen Nhat Anh", 1990, 4),
    ("9786041234604", "Nha Gia Kim", "Paulo Coelho", 1988, 2),
    ("9786041234611", "Cho Toi Xin Mot Ve Di Tuoi Tho", "Nguyen Nhat Anh", 2008, 4),
    ("9786041234628", "Nhung Nguoi Khon Kho", "Victor Hugo", 1862, 1),
    ("9786041234635", "Toi Thay Hoa Vang Tren Co Xanh", "Nguyen Nhat Anh", 2010, 3),
    ("9786041234642", "Chi Pheo", "Nam Cao", 1941, 3),
    ("9786041234659", "Tat Den", "Ngo Tat To", 1937, 2),
    ("9786041234666", "Nguyen Ngoc Tu - Canh Dong Bat Tan", "Nguyen Ngoc Tu", 2005, 2),
    ("9786041234673", "Hoang Tu Be", "Antoine de Saint-Exupery", 1943, 4),
    ("9786041234680", "Dac Nhan Tam", "Dale Carnegie", 1936, 5),
    ("9786041234697", "Nha Lanh Dao Khong Chuc Danh", "Robin Sharma", 2010, 1),
    ("9786041234703", "Lap Trinh Python Co Ban", "Nguyen Van Hung", 2021, 6),
    ("9786041234710", "Cau Truc Du Lieu Va Giai Thuat", "Tran Minh Duc", 2019, 4),
    ("9786041234727", "Co So Du Lieu Quan He", "Le Thi Lan", 2020, 3),
    ("9786041234734", "Mang May Tinh Can Ban", "Pham Quoc Bao", 2018, 2),
]

DOC_GIA_MAU = [
    ("DG001", "Nguyen Van An", "an.nguyen@thuvien.vn", True),
    ("DG002", "Tran Thi Binh", "binh.tran@thuvien.vn", True),
    ("DG003", "Le Minh Cuong", "cuong.le@thuvien.vn", True),
    ("DG004", "Pham Thu Dung", "dung.pham@thuvien.vn", True),
    ("DG005", "Hoang Van Em", "em.hoang@thuvien.vn", True),
    ("DG006", "Vo Thi Giang", "giang.vo@thuvien.vn", True),
    ("DG007", "Bui Quoc Hung", "hung.bui@thuvien.vn", False),   # the bi khoa
    ("DG008", "Dang Thi Lan", "lan.dang@thuvien.vn", True),
    ("DG009", "Do Van Minh", "minh.do@thuvien.vn", True),
    ("DG010", "Ngo Thi Nga", "nga.ngo@thuvien.vn", True),
]

# (chi so sach, chi so doc gia, so ngay truoc, da tra chua)
LICH_SU_MUON = [
    (14, 0, 40, True), (14, 1, 32, True), (14, 2, 25, True), (14, 3, 12, True),
    (15, 0, 30, True), (15, 4, 18, True), (15, 5, 9, True),
    (3, 1, 27, True), (3, 6, 20, True),
    (12, 2, 22, True), (12, 7, 15, True),
    (0, 8, 35, True),
    (16, 3, 20, False), (2, 9, 16, False), (7, 4, 10, False),
    (5, 5, 6, False), (13, 8, 3, False),
]


def khoi_tao_du_lieu():
    if not cau_hinh.tao_du_lieu_mau:
        return
    db = SessionLocal()
    try:
        if db.query(NguoiDung).count() == 0:
            db.add_all(
                NguoiDung(
                    ten_dang_nhap=ten,
                    mat_khau_ma_hoa=bam_mat_khau(mat_khau),
                    la_thu_thu=la_thu_thu,
                )
                for ten, mat_khau, la_thu_thu in TAI_KHOAN
            )
            db.commit()

        if db.query(Sach).count() > 0:
            return

        cac_sach = [
            Sach(
                isbn=isbn,
                tieu_de=tieu_de,
                tac_gia=tac_gia,
                nam_xuat_ban=nam,
                so_ban=so_ban,
                so_ban_con=so_ban,
            )
            for isbn, tieu_de, tac_gia, nam, so_ban in SACH_MAU
        ]
        cac_doc_gia = [
            DocGia(ma_dg=ma, ho_ten=ten, email=mail, dang_hoat_dong=hoat_dong)
            for ma, ten, mail, hoat_dong in DOC_GIA_MAU
        ]
        db.add_all(cac_sach)
        db.add_all(cac_doc_gia)
        db.flush()          # can id cua sach va doc gia de tao phieu muon

        hom_nay = date.today()
        for i_sach, i_doc_gia, so_ngay_truoc, da_tra in LICH_SU_MUON:
            sach = cac_sach[i_sach]
            ngay_muon = hom_nay - timedelta(days=so_ngay_truoc)
            han_tra = ngay_muon + timedelta(days=cau_hinh.so_ngay_duoc_muon)
            phieu = PhieuMuon(
                sach_id=sach.id,
                doc_gia_id=cac_doc_gia[i_doc_gia].id,
                ngay_muon=ngay_muon,
                han_tra=han_tra,
            )
            if da_tra:
                ngay_tra = min(han_tra + timedelta(days=1), hom_nay)
                phieu.ngay_tra = ngay_tra
                so_ngay_tre = (ngay_tra - han_tra).days
                phieu.tien_phat = max(0, so_ngay_tre) * cau_hinh.tien_phat_moi_ngay
            else:
                sach.so_ban_con -= 1     # dang muon thi tru ban con lai
            db.add(phieu)

        db.commit()
    finally:
        db.close()
