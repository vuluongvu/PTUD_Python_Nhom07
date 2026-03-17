# LapStore - Website Bán Laptop & Linh Kiện

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-darkgreen?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-gray?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)

## 1. Mục tiêu dự án

Xây dựng một trang web thương mại điện tử hoàn chỉnh, chuyên nghiệp để kinh doanh laptop và linh kiện máy tính. Dự án tập trung vào trải nghiệm người dùng mượt mà, giao diện hiện đại và tích hợp các công nghệ mới như AI chatbot và cổng thanh toán trực tuyến.

## 2. Kiến trúc & Công nghệ

### Kiến trúc

Dự án được xây dựng theo kiến trúc module hóa của Django, bao gồm các ứng dụng chính:

- `core`: Chứa các model, view và logic chung (trang chủ, chatbot, layout cơ bản).
- `products`: Quản lý thông tin sản phẩm, danh mục, tìm kiếm và bộ lọc.
- `users`: Xử lý xác thực, hồ sơ người dùng, quản lý địa chỉ.
- `orders`: Quản lý giỏ hàng, quy trình thanh toán, đơn hàng và tích hợp cổng thanh toán.

### Công nghệ sử dụng

- **Backend:**
  - **Ngôn ngữ:** Python 3.10+
  - **Framework:** Django 5.0+
  - **API:** Django REST Framework (cho các API nội bộ)
  - **Server:** Gunicorn (cho production)
- **Frontend:**
  - HTML5, CSS3, JavaScript (ES6+)
  - **Thư viện:** Swiper.js (cho sliders), SweetAlert2 (cho thông báo)
- **Cơ sở dữ liệu:**
  - **Production:** PostgreSQL (khuyến nghị)
  - **Development:** SQLite3
- **Dịch vụ bên thứ ba:**
  - **Thanh toán:** MoMo API (tích hợp qua `momo_service`)
  - **AI Chatbot:** Google Gemini API (`google-generativeai`)
  - **Lưu trữ ảnh:** ImgBB API (để upload avatar và ảnh sản phẩm)
- **Deployment:**
  - `whitenoise`: Phục vụ file tĩnh.
  - `dj-database-url`: Cấu hình database từ URL.
  - `python-dotenv`: Quản lý biến môi trường.

## 3. Hướng dẫn Cài đặt & Khởi chạy

**Yêu cầu:**

- Python 3.10 trở lên
- Git
- PostgreSQL (khuyến nghị cho môi trường giống production)

**Các bước cài đặt:**

1.  **Clone repository:**

    ```bash
    git clone https://github.com/your-username/Laptop_Store.git
    cd Laptop_Store
    ```

2.  **Tạo và kích hoạt môi trường ảo:**

    ```bash
    # Windows (PowerShell)
    python -m venv env
    .\env\Scripts\Activate.ps1

    # macOS/Linux
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình biến môi trường:**
    Tạo một file tên là `.env` trong thư mục gốc của dự án (cùng cấp với `manage.py`) và thêm các biến sau.
    _Lưu ý: Thay thế các giá trị `your_...` bằng khóa API thực tế của bạn.\_

    ```env
    # Django
    SECRET_KEY='your_django_secret_key' # Tạo một chuỗi ngẫu nhiên, mạnh
    DEBUG=True

    # Database (Ví dụ cho PostgreSQL)
    DATABASE_URL='postgres://user:password@host:port/dbname'

    # Google Gemini API
    GOOGLE_API_KEY='your_google_api_key'

    # ImgBB API (dùng để upload avatar)
    IMGBB_API_KEY='your_imgbb_api_key'

    # MoMo Payment Gateway (Sandbox)
    MOMO_PARTNER_CODE='your_momo_partner_code'
    MOMO_ACCESS_KEY='your_momo_access_key'
    MOMO_SECRET_KEY='your_momo_secret_key'
    MOMO_API_ENDPOINT='https://test-payment.momo.vn/v2/gateway/api/create'
    MOMO_REDIRECT_URL='http://127.0.0.1:8000/orders/momo/return/'
    MOMO_IPN_URL='your_public_ipn_handler_url' # Cần ngrok để test trên localhost
    ```

5.  **Chạy Database Migrations:**
    Lệnh này sẽ tạo các bảng trong cơ sở dữ liệu dựa trên models của Django.

    ```bash
    python manage.py migrate
    ```

6.  **Tạo Superuser (Tài khoản Admin):**
    Tài khoản này dùng để truy cập vào trang quản trị (`/admin`).

    ```bash
    python manage.py createsuperuser
    ```

    _Sau đó nhập username, email và mật khẩu._

7.  **Khởi chạy Server:**
    ```bash
    python manage.py runserver
    ```
    Ứng dụng sẽ chạy tại địa chỉ: `http://127.0.0.1:8000/`

## 4. Tài khoản mẫu

Bạn có thể sử dụng tài khoản đã tạo ở bước 6 để đăng nhập và trải nghiệm các tính năng hoặc truy cập trang quản trị.

- **Trang quản trị:** `http://127.0.0.1:8000/admin/`
- **Username:** (username bạn đã tạo)
- **Password:** (mật khẩu bạn đã tạo)
