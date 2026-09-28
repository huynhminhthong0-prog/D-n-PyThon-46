# API Thư viện — dự án mẫu để deploy

API quản lý mượn trả sách của một thư viện nhỏ. Hai vai:

**Một — bản tổng hợp cả khoá.** Không chỉ phần FastAPI: **kiến thức lập trình cơ bản**
(vòng lặp, `if`, hàm, list/dict), **đọc ghi file** (CSV và JSON), **OOP** (lớp trừu tượng,
kế thừa, đa hình), **SQL** (`JOIN`, `GROUP BY`, hàm tổng hợp) và **FastAPI** (validate, mã
trạng thái, ORM, migration, quan hệ, transaction, dependency injection, router, JWT) — tất cả
nằm trong một dự án chạy được. Xem [bản đồ kiến thức](#bản-đồ-kiến-thức) để biết chỗ nào là
của buổi nào.

**Hai — dự án để tập deploy.** Code đã viết xong và chạy được, nên hôm nay bạn không phải
vừa sửa bug vừa học deploy. Việc của bạn là đưa nó lên internet.

## Chạy trên máy trong 5 phút

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # rồi mở ra sửa KHOA_BI_MAT
python -c "import secrets; print(secrets.token_urlsafe(48))"

alembic upgrade head               # tạo bảng
fastapi dev app/main.py
```

Mở `http://127.0.0.1:8000/docs`.

Dữ liệu mẫu nạp sẵn: **18 đầu sách** (56 bản), **10 độc giả**, và **17 phiếu mượn** rải trong
40 ngày qua — trong đó có phiếu đang quá hạn và một thẻ bị khoá. Đủ để `/thong-ke` ra số có
nghĩa ngay lần đầu mở.

Hai tài khoản có sẵn:

| Tài khoản | Mật khẩu | Quyền |
|---|---|---|
| `thuthu` | `thuthu123` | Thủ thư — làm được mọi thứ |
| `khach` | `khach123` | Khách — chỉ xem sách |

Bấm **Authorize** ở góc trên bên phải trang `/docs`, đăng nhập bằng `thuthu`, rồi thử các
endpoint.

## Nó làm được gì

| Nhóm | Endpoint | Quyền |
|---|---|---|
| Xác thực | `POST /auth/dang-ky`, `POST /auth/dang-nhap`, `GET /auth/toi` | công khai |
| Sách | `GET /sach`, `GET /sach/{id}` | công khai |
| | `POST /sach`, `PUT /sach/{id}`, `DELETE /sach/{id}` | thủ thư |
| Độc giả | `GET/POST/PUT /doc-gia`, `GET /doc-gia/{id}/dang-muon` | thủ thư |
| Mượn trả | `GET /muon-tra`, `POST /muon-tra/muon`, `POST /muon-tra/tra/{id}` | thủ thư |
| Thống kê | `GET /thong-ke`, `GET /thong-ke/sach-muon-nhieu` | công khai |
| | `GET /thong-ke/qua-han` | thủ thư |
| Nhập xuất file | `GET /nhap-xuat/sach.csv`, `GET /nhap-xuat/bao-cao.json` | công khai |
| | `POST /nhap-xuat/sach.csv` (tải file CSV lên) | thủ thư |
| Hệ thống | `GET /health` | công khai |

`GET /sach` có tìm kiếm theo tiêu đề hoặc tác giả (`?tim=`), lọc sách còn bản
(`?con_hang=true`), và phân trang (`?bo_qua=&gioi_han=`).

Ba endpoint thống kê là chỗ SQL "nặng" nhất của dự án:

```
GET /thong-ke
{"so_dau_sach":18,"so_ban_sach":56,"so_doc_gia":10,
 "so_phieu_dang_muon":5,"so_phieu_qua_han":2,"tong_tien_phat":50000}

GET /thong-ke/sach-muon-nhieu?gioi_han=5          JOIN + GROUP BY + COUNT
 4  Lap Trinh Python Co Ban          Nguyen Van Hung
 3  Cau Truc Du Lieu Va Giai Thuat   Tran Minh Duc
 2  Dac Nhan Tam                     Dale Carnegie
 2  Mat Biec                         Nguyen Nhat Anh
 1  Cho Toi Xin Mot Ve Di Tuoi Tho   Nguyen Nhat Anh

GET /thong-ke/qua-han   [thu thu]                 viet bang SQL tay
[{"ma_dg":"DG004","ho_ten":"Pham Thu Dung","tieu_de":"Co So Du Lieu Quan He","han_tra":"2026-08-22"},
 {"ma_dg":"DG010","ho_ten":"Ngo Thi Nga","tieu_de":"De Men Phieu Luu Ky","han_tra":"2026-08-26"}]
```

`/thong-ke` dùng `func.sum` để database cộng giúp, không kéo cả bảng về Python rồi `sum()`.
`/thong-ke/sach-muon-nhieu` dùng `LEFT JOIN` để sách chưa ai mượn vẫn hiện ra với `so_luot_muon: 0`.
`/thong-ke/qua-han` cố ý viết bằng SQL tay qua `text()` — có những câu ba bảng đọc ở dạng SQL
dễ hơn hẳn dạng ORM, và tham số vẫn truyền qua `:ten` chứ không nối chuỗi.

## Nhập và xuất file

Thủ thư thật không ngồi gõ tay 500 đầu sách vào `/docs`. Họ có sẵn một file Excel.

```
GET  /nhap-xuat/sach.csv          tai toan bo danh muc ve
POST /nhap-xuat/sach.csv          tai mot file CSV len de nhap hang loat  [thu thu]
GET  /nhap-xuat/bao-cao.json      bao cao tong hop dang JSON
```

```
$ curl -O https://.../nhap-xuat/sach.csv
isbn,tieu_de,tac_gia,nam_xuat_ban,so_ban,so_ban_con
9786041234567,Doi Mua Bui,Duyen Anh,1992,3,3
9786041234574,So Do,Vu Trong Phung,1936,2,2
9786041234581,De Men Phieu Luu Ky,To Hoai,1941,5,4
...

$ curl -X POST -H "Authorization: Bearer $TOKEN" -F "file=@sach-moi.csv" .../nhap-xuat/sach.csv
{"da_them":2,"bo_qua_vi_trung_isbn":["9786041234567"]}
```

`app/nhap_xuat.py` chỉ làm việc với **chuỗi và list/dict** — không đụng tới FastAPI hay
database. Nhờ vậy `doc_sach_tu_csv()` test được thẳng, không cần dựng server.

Bốn chi tiết của việc đọc file người khác gửi, và dự án lo cả bốn:

| Tình huống | Xử lý |
|---|---|
| File không phải `.csv` | `422 Chi nhan file .csv` |
| File quá lớn | `413`, chặn ở 1 MB |
| File lưu bằng mã khác UTF-8 | `422 File phai luu bang ma UTF-8` |
| File Excel có BOM ở đầu | `decode("utf-8-sig")` tự bỏ |
| Thiếu cột bắt buộc | `422 File CSV thieu cot: isbn, tac_gia` |
| Một dòng trống hoặc thiếu dữ liệu | Bỏ qua dòng đó, các dòng khác vẫn nhập |
| Một dòng trùng ISBN | `rollback` dòng đó, báo lại trong `bo_qua_vi_trung_isbn` |

Nhập 100 dòng mà dòng 47 trùng ISBN thì 99 dòng kia vẫn vào. Đó là điểm khác giữa một
endpoint dùng được và một endpoint chỉ chạy khi dữ liệu sạch.

## Quy tắc nghiệp vụ viết bằng OOP

`app/nghiep_vu.py` có hai họ lớp. Đây là chỗ OOP có ích thật, không phải cho có.

**`QuyTacMuon`** — lớp trừu tượng (`ABC`), mỗi điều kiện cho mượn là một lớp con:

```python
class QuyTacMuon(ABC):
    ly_do: str = "Khong dat dieu kien muon"

    @abstractmethod
    def dat(self, ngu_canh: NguCanhMuon) -> bool: ...

    def kiem_tra(self, ngu_canh: NguCanhMuon) -> None:
        if not self.dat(ngu_canh):
            raise HTTPException(status_code=409, detail=self.mo_ta(ngu_canh))


class ConBanDeMuon(QuyTacMuon):
    ly_do = "Sach da het ban de muon"

    def dat(self, ngu_canh: NguCanhMuon) -> bool:
        return ngu_canh.sach.so_ban_con > 0
```

`crud.muon_sach` không biết có bao nhiêu quy tắc, cũng không biết chúng làm gì:

```python
for quy_tac in QUY_TAC_CHO_MUON:
    quy_tac.kiem_tra(ngu_canh)
```

Thêm quy tắc mới = **thêm một lớp** rồi ghi tên nó vào danh sách. Không sửa dòng nào trong
`crud.py`. So với một hàm 40 dòng toàn `if ... raise` nối nhau.

**`ChinhSachPhat`** — cách tính tiền phạt, đổi được bằng cấu hình:

```python
>>> PhatTheoNgay(5000).tinh(10)      # moi ngay 5.000d
50000
>>> PhatBacThang(5000).tinh(10)      # 7 ngay dau 5.000d, tu ngay 8 gap doi
65000
>>> PhatBacThang(5000).tinh(-2)      # tra som khong duoc thuong
0
```

`CHINH_SACH_PHAT=bac_thang` trong `.env` là đổi cách tính. `crud.tra_sach` không đổi một chữ
— nó gọi `chinh_sach.tinh(so_ngay_tre)` và không quan tâm object đó thuộc lớp nào. Đó là
**đa hình**, và đây là lý do người ta dùng nó.

## Danh sách quy tắc nghiệp vụ

Đây là phần làm nó khác một bài CRUD thường. Mọi quy tắc đều cấu hình được qua `.env`:

| Quy tắc | Vi phạm thì | Cấu hình |
|---|---|---|
| Sách hết bản thì không mượn được | `409 Sach da het ban de muon` | |
| Mỗi độc giả giữ tối đa 3 cuốn | `409 Moi doc gia chi duoc giu toi da 3 cuon` | `SO_SACH_TOI_DA` |
| Không mượn hai lần cùng một cuốn | `409 Doc gia dang muon cuon nay roi` | |
| Thẻ bị khoá thì không mượn được | `409 The doc gia dang bi khoa` | |
| Hạn trả 14 ngày kể từ ngày mượn | | `SO_NGAY_DUOC_MUON` |
| Trả trễ bị phạt 5.000đ mỗi ngày | tính vào `tien_phat` | `TIEN_PHAT_MOI_NGAY`, `CHINH_SACH_PHAT` |
| Phiếu đã trả thì không trả lại | `409 Phieu nay da tra roi` | |
| Sách đang có người mượn thì không xoá | `409 Sach dang duoc muon, khong xoa duoc` | |
| Không giảm `so_ban` xuống dưới số đang cho mượn | `409` | |

Mượn thì `so_ban_con` giảm 1, trả thì tăng 1 — hai việc nằm trong **cùng một transaction**,
nên không bao giờ có chuyện ghi phiếu xong mà quên trừ số bản.

## Cấu trúc

```
du-an-mau/
├── app/
│   ├── main.py          lắp router, CORS, /health, /thong-ke
│   ├── config.py        đọc mọi cấu hình từ biến môi trường
│   ├── database.py      engine, SessionLocal, Base
│   ├── models.py        4 bảng: nguoi_dung, sach, doc_gia, phieu_muon
│   ├── schemas.py       JSON vào / ra
│   ├── crud.py          truy vấn + điều phối nghiệp vụ
│   ├── nghiep_vu.py     OOP — lớp trừu tượng quy tắc mượn, chính sách phạt
│   ├── nhap_xuat.py     đọc ghi file CSV và JSON
│   ├── deps.py          lay_db()
│   ├── auth.py          bcrypt, JWT, phân quyền
│   ├── seed.py          dữ liệu mẫu — 18 sách, 10 độc giả, 17 phiếu mượn
│   └── routers/         auth, sach, doc_gia, muon_tra, nhap_xuat
├── alembic/             migration — cấu trúc bảng
├── tests/test_api.py    13 test chạy trên database trong RAM
├── .env.example         mẫu cấu hình, chép thành .env
├── .python-version      ghim Python 3.13 cho Render
├── render.yaml          để deploy lên Render
└── requirements.txt     đã ghim version
```

## Bản đồ kiến thức

Dự án này không có kiến thức mới. Nó là chỗ mọi thứ đã học gặp nhau — mở file tương ứng ra
là thấy lại đúng thứ mình từng làm:

| Học ở buổi | Trong dự án nằm ở đâu |
|---|---|
| Lập trình cơ bản: `if`, `for`, hàm, list/dict | `nhap_xuat.doc_sach_tu_csv`, `crud.thong_ke`, khắp nơi |
| Đọc ghi file văn bản | `nhap_xuat.luu_ra_file` — `open(..., encoding="utf-8")` |
| Đọc ghi CSV | `nhap_xuat.doc_sach_tu_csv`, `ghi_sach_ra_csv` — `csv.DictReader` / `DictWriter` |
| Đọc ghi JSON | `nhap_xuat.ghi_bao_cao_json` — `json.dumps` với `default=` cho `date` |
| OOP: lớp, kế thừa, đa hình, `ABC` | `app/nghiep_vu.py` — `QuyTacMuon` và `ChinhSachPhat` |
| OOP: `@dataclass`, `__repr__` | `NguCanhMuon`, `__repr__` trong mọi model |
| FastAPI, `/docs`, mã trạng thái | `app/main.py`, mọi router — 200/201/204/401/403/404/409/422 |
| Path & query parameter | `Path(gt=0)`, `Query(default=20, ge=1, le=100)` trong `routers/sach.py` |
| Pydantic — validate dữ liệu vào | `app/schemas.py`: `Field(pattern=r"^DG\d{3,}$")`, `EmailStr`, `ge`/`le` |
| CRUD đầy đủ, `exclude_unset` | `crud.sua_sach`, `crud.sua_doc_gia` |
| SQL: `JOIN`, `GROUP BY`, `COUNT` | `crud.sach_muon_nhieu`, `crud.doc_gia_qua_han` (SQL tay qua `text()`) |
| SQLAlchemy — model, session | `app/models.py`, `app/database.py` |
| Migration bằng Alembic | `alembic/versions/`, lệnh khởi động có `alembic upgrade head` |
| Quan hệ 1-n, `cascade` | `Sach.phieu_muon`, `DocGia.phieu_muon`, `PhieuMuon.sach` |
| Transaction, `rollback`, `409` | `crud.tao_sach`, `crud.muon_sach` — trừ `so_ban_con` cùng transaction với ghi phiếu |
| `selectinload` chống N+1 | `crud.liet_ke_phieu` |
| Dependency injection | `app/deps.py`, `Depends(lay_db)` ở mọi endpoint |
| `APIRouter`, cấu trúc `app/` | `app/routers/` — 4 router |
| JWT, bcrypt, 401 vs 403 | `app/auth.py`, `routers/auth.py`, `dependencies=[Depends(chi_thu_thu)]` |
| Cấu hình & deploy | `app/config.py`, `.env.example`, `render.yaml` |
| Kiểm thử | `tests/test_api.py` — `dependency_overrides` + SQLite trong RAM |

Thứ **duy nhất** dự án có mà chưa buổi nào dạy là các quy tắc nghiệp vụ ở bảng trên. Đó cũng
là phần bạn phải tự nghĩ ra khi làm đề tài của mình.

## Cấu hình

Mọi giá trị trong `app/config.py` đọc được từ biến môi trường. Tên biến viết HOA, trùng tên
thuộc tính.

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `CHUOI_KET_NOI` | `sqlite:///./thu_vien.db` | Đường tới database |
| `KHOA_BI_MAT` | *(chuỗi nhắc đổi)* | Khoá ký JWT — **bắt buộc đổi** |
| `SO_PHUT_HET_HAN` | `30` | Hạn của token |
| `NGUON_CHO_PHEP` | `*` | CORS, ngăn nhau bằng dấu phẩy |
| `TIEN_PHAT_MOI_NGAY` | `5000` | Tiền phạt trả trễ (đồng) |
| `CHINH_SACH_PHAT` | `theo_ngay` | `theo_ngay` hoặc `bac_thang` |
| `SO_NGAY_DUOC_MUON` | `14` | Hạn trả |
| `SO_SACH_TOI_DA` | `3` | Số cuốn một người được giữ |
| `TAO_DU_LIEU_MAU` | `true` | Nạp sách và tài khoản mẫu. Production thật thì đặt `false` |

**File `.env` không bao giờ được commit.** `.gitignore` đã chặn sẵn.

## Chạy test

```bash
pip install -r requirements-dev.txt
pytest -q
```

```
12 passed
```

Test chạy trên `sqlite://` trong RAM qua `dependency_overrides`, nên không đụng tới
`thu_vien.db`.

## Đổi database

Không sửa dòng code nào, chỉ đổi một biến môi trường:

```
CHUOI_KET_NOI=postgresql+psycopg://user:matkhau@host:5432/thu_vien
```

`app/database.py` có hàm `chuan_hoa()` xử lý một chi tiết dễ mất thời gian: Render cấp chuỗi
bắt đầu bằng `postgres://`, mà SQLAlchemy 2.0 chỉ hiểu `postgresql://`. Bỏ hàm đó đi thì
deploy lỗi `NoSuchModuleError`.

## Ghi chú kỹ thuật

`tien_phat` dùng `Integer` vì đơn vị là đồng, không có phần lẻ. Tiền có phần lẻ (USD, EUR)
thì phải dùng `Numeric`, **không bao giờ dùng `Float`**.

`pool_pre_ping=True` trong `create_engine`: nền tảng miễn phí hay ngắt kết nối database đang
rảnh. Tham số này kiểm tra kết nối trước khi dùng, và mở lại nếu nó đã chết.

`Base.metadata.create_all()` **không** được gọi ở đâu cả. Cấu trúc bảng do Alembic quản, một
mình. Chạy `alembic upgrade head` trước khi khởi động app.

Dự án **không dùng Docker**. Render chạy Python trực tiếp, nên `requirements.txt` và
`startCommand` là đủ.
