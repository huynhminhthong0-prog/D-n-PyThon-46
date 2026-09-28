from pydantic_settings import BaseSettings, SettingsConfigDict


class CauHinh(BaseSettings):
    """Moi gia tri deu doc duoc tu bien moi truong hoac file .env.

    Ten bien moi truong viet HOA, trung ten thuoc tinh: CHUOI_KET_NOI, KHOA_BI_MAT...
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ten_ung_dung: str = "API Thu Vien"
    chuoi_ket_noi: str = "sqlite:///./thu_vien.db"
    khoa_bi_mat: str = "doi-khoa-nay-truoc-khi-deploy"
    so_phut_het_han: int = 30
    nguon_cho_phep: str = "*"
    tien_phat_moi_ngay: int = 5000
    chinh_sach_phat: str = "theo_ngay"   # hoac "bac_thang"
    so_ngay_duoc_muon: int = 14
    so_sach_toi_da: int = 3
    tao_du_lieu_mau: bool = True


cau_hinh = CauHinh()
