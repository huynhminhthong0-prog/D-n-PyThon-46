from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud
from app.config import cau_hinh
from app.deps import lay_db
from app.routers import auth, doc_gia, muon_tra, nhap_xuat, sach
from app.auth import chi_thu_thu
from app.schemas import PhieuQuaHan, SachXepHang, ThongKe
from app.seed import khoi_tao_du_lieu

app = FastAPI(
    title=cau_hinh.ten_ung_dung,
    version="1.0.0",
    description="API quan ly muon tra sach cua mot thu vien nho.",
)

app.add_middleware(
    
    CORSMiddleware,
    allow_origins=[n.strip() for n in cau_hinh.nguon_cho_phep.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

khoi_tao_du_lieu()

app.include_router(auth.router)
app.include_router(sach.router)
app.include_router(doc_gia.router)
app.include_router(muon_tra.router)
app.include_router(nhap_xuat.router)


@app.get("/health", tags=["He thong"])
async def health(db: Session = Depends(lay_db)):
    """Render goi duong dan nay de biet app con song."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "ten": cau_hinh.ten_ung_dung}


@app.get("/thong-ke", response_model=ThongKe, tags=["Thong ke"])
async def thong_ke(db: Session = Depends(lay_db)):
    return crud.thong_ke(db)


@app.get("/thong-ke/sach-muon-nhieu", response_model=list[SachXepHang], tags=["Thong ke"])
async def sach_muon_nhieu(
    gioi_han: int = Query(default=5, ge=1, le=50), db: Session = Depends(lay_db)
):
    """Xep hang sach theo so luot muon — JOIN + GROUP BY + COUNT."""
    return crud.sach_muon_nhieu(db, gioi_han)


@app.get(
    "/thong-ke/qua-han",
    response_model=list[PhieuQuaHan],
    tags=["Thong ke"],
    dependencies=[Depends(chi_thu_thu)],
)
async def qua_han(db: Session = Depends(lay_db)):
    """Danh sach doc gia dang giu sach qua han — viet bang SQL tay."""
    return crud.doc_gia_qua_han(db)
