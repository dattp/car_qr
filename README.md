# QR Code Generator cho Xe

Desktop app: chọn file Excel chứa thông tin xe → tạo trang HTML cho từng xe + file PDF chứa QR codes.

## Tính năng

- Đọc file Excel format chuẩn (sheet `Lịch bảo dưỡng (2)`, 17 cột)
- Sinh 1 file HTML cho mỗi xe (đẹp, mobile-friendly)
- Sinh PDF A4, 12 QR/trang, mỗi QR trỏ tới trang HTML tương ứng
- Hỗ trợ macOS + Windows

## Chạy local (cần Python 3.10+)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

## Build .app / .exe trên máy mình

```bash
.venv/bin/pip install pyinstaller
.venv/bin/pyinstaller --noconfirm --clean --windowed --name "QR Generator" main.py
# Mac: ra dist/QR Generator.app
# Win: ra dist/QR Generator.exe
```

## Build cho cả Mac & Windows qua GitHub Actions (khuyến nghị)

### Lần đầu setup (~10 phút)

1. Đăng ký tài khoản https://github.com (free)
2. Tạo repo mới → đặt tên (vd `qr-xe-generator`) → **Public** (free) → bấm Create
3. Trên trang repo, bấm **uploading an existing file** → kéo-thả toàn bộ folder này vào (trừ `.venv/`, `dist/`, `qr_codes.pdf`)
4. Commit → GitHub Actions tự chạy

### Lấy file binary

- Cách 1 (đơn giản): vào tab **Actions** → click vào lần build mới nhất → kéo xuống cuối có **Artifacts** → tải `QR-Generator-macOS` và `QR-Generator-Windows`
- Cách 2 (release chính thức): tạo 1 tag `v1.0.0`:
  - Trên web repo, bấm **Releases** → **Draft a new release** → tag `v1.0.0` → Publish
  - GitHub Actions build xong sẽ tự upload `.zip` vào release đó

### Cài đặt cho user

- **macOS**: giải nén → kéo `QR Generator.app` vào `Applications` → **right-click → Open** (lần đầu, vì chưa ký số)
- **Windows**: giải nén → mở folder `QR Generator/` → double-click `QR Generator.exe` → nếu SmartScreen cảnh báo: **More info → Run anyway**. Lưu ý: không tách `.exe` ra khỏi folder, nó cần các file DLL bên trong để chạy.

## Quy trình dùng app

1. Mở app
2. **File Excel**: chọn file
3. **Subdomain Netlify**: nhập tên site (vd `qr-xe` → URL `https://qr-xe.netlify.app`)
4. **Thư mục xuất**: chọn folder (mặc định: cùng folder với Excel)
5. Bấm **Tạo QR Code**
6. Khi xong: bấm **Mở Netlify Drop** → kéo thả folder `dist/` lên đó
7. Bấm **Mở PDF** → in → cắt → dán lên xe

## Lưu ý

- Tên subdomain Netlify phải khớp với URL trong QR. Nếu đổi subdomain → phải tạo lại QR.
- Update data: chỉ cần chạy lại app, upload lại `dist/` lên Netlify (đè site cũ). QR cũ vẫn dùng tốt.
