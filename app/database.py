from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import cau_hinh


def chuan_hoa(url: str) -> str:
    """Ep chuoi ket noi Postgres ve dung driver psycopg 3.

    Render cap chuoi bat dau bang 'postgres://' (kieu cu) hoac 'postgresql://'
    (kieu hien nay). Ca hai deu khong noi ro driver: 'postgres' thi SQLAlchemy 2.0
    khong con hieu, con 'postgresql' thi no mac dinh chon psycopg2 — goi ma du an
    nay khong cai. Chi 'postgresql+psycopg://' moi tro dung psycopg 3.

    Chuoi da ghi ro driver ('postgresql+psycopg2://'...) thi giu nguyen.
    """
    for tien_to in ("postgres://", "postgresql://"):
        if url.startswith(tien_to):
            return "postgresql+psycopg://" + url[len(tien_to):]
    return url


CHUOI_KET_NOI = chuan_hoa(cau_hinh.chuoi_ket_noi)

# check_same_thread la tham so rieng cua SQLite; Postgres khong hieu no
tham_so_rieng = (
    {"check_same_thread": False} if CHUOI_KET_NOI.startswith("sqlite") else {}
)

engine = create_engine(
    CHUOI_KET_NOI, connect_args=tham_so_rieng, pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass
