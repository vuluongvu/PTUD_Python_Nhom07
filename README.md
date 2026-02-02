# Laptop_Store

Ứng dụng cửa hàng laptop đơn giản xây dựng bằng Django.

## Giới thiệu

- Mô tả: Hệ thống quản lý sản phẩm (laptop, phụ kiện), người dùng, và đơn hàng.
- Cấu trúc chính: ứng dụng `core`, `products`, `orders`, `users`.

## Yêu cầu

- Python 3.10+ (hoặc phiên bản phù hợp với `env` trong repo)
- Django 6.x

## Cài đặt nhanh (Windows)

1. Tạo virtualenv và kích hoạt (nếu chưa có):

```powershell
python -m venv env
env\Scripts\Activate.ps1    # PowerShell
# hoặc env\Scripts\activate.bat cho cmd
```

2. Cài dependencies (nếu có file requirements.txt):

```powershell
pip install -r requirements.txt
```

3. Chạy migrations và tạo superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Chạy server phát triển:

```powershell
python manage.py runserver
```

Mở trình duyệt `http://127.0.0.1:8000/` để xem ứng dụng.

## Cấu hình cơ sở dữ liệu

- Hiện tại dự án sử dụng SQLite (`db.sqlite3`) theo mặc định.
- Để đổi sang PostgreSQL/MySQL, chỉnh `DATABASES` trong `webbapp/settings.py`.

## Tính năng chính

- Quản lý sản phẩm (danh sách, chi tiết)
- Giỏ hàng, thanh toán cơ bản
- Quản lý người dùng và hồ sơ

## Chạy test

```powershell
python manage.py test
```

## Đóng góp

- Fork repo, tạo branch mới cho tính năng/bugfix, gửi pull request.
- Vui lòng viết rõ mô tả, kèm hướng dẫn chạy nếu cần.

## Liên hệ

- Thêm hướng dẫn liên hệ hoặc issues trên repository nếu muốn.

---

_README này là bản tóm tắt nhanh; tôi có thể mở rộng thêm phần hướng dẫn cấu hình môi trường, CI, hoặc hướng dẫn triển khai nếu bạn muốn._
