"""
MoMo Payment Service
====================
Service module xử lý tích hợp cổng thanh toán MoMo (Sandbox).

Luồng hoạt động:
1. Tạo chữ ký HMAC-SHA256 từ dữ liệu đơn hàng
2. Gửi request tới MoMo API để lấy payUrl
3. Redirect người dùng tới trang thanh toán MoMo
4. Xác minh chữ ký khi MoMo callback (return URL / IPN)

MoMo API Docs: https://developers.momo.vn/v3/docs/payment/api/wallet/onetime
"""

import uuid
import hmac
import hashlib
import requests
from django.conf import settings


def create_momo_payment(order_id, amount, order_info="Thanh toán đơn hàng LapStore"):
    """
    Tạo yêu cầu thanh toán MoMo.
    
    Args:
        order_id (int): ID của đơn hàng trong hệ thống
        amount (int): Số tiền cần thanh toán (VNĐ, số nguyên)
        order_info (str): Mô tả đơn hàng hiển thị trên trang MoMo
    
    Returns:
        dict: Response từ MoMo API, bao gồm:
            - payUrl: URL trang thanh toán MoMo (redirect user tới đây)
            - resultCode: 0 = thành công tạo request
            - message: Thông báo từ MoMo
    
    Ví dụ JSON gửi tới MoMo API:
    {
        "partnerCode": "MOMOBKUN20180529",
        "accessKey": "klm05TvNBzhg7h7j",
        "requestId": "unique-uuid-string",
        "amount": 50000,
        "orderId": "LAPSTORE_42_uuid",
        "orderInfo": "Thanh toán đơn hàng LapStore",
        "redirectUrl": "http://localhost:8000/momo/return/",
        "ipnUrl": "http://localhost:8000/momo/ipn/",
        "extraData": "",
        "requestType": "payWithMethod",
        "signature": "hmac_sha256_hash_string",
        "lang": "vi"
    }
    """
    
    # ====== 1. Lấy thông tin cấu hình từ settings ======
    partner_code = settings.MOMO_PARTNER_CODE
    access_key = settings.MOMO_ACCESS_KEY
    secret_key = settings.MOMO_SECRET_KEY
    endpoint = settings.MOMO_API_ENDPOINT
    redirect_url = settings.MOMO_REDIRECT_URL
    ipn_url = settings.MOMO_IPN_URL
    
    # ====== 2. Tạo các tham số cho request ======
    # request_id: ID duy nhất cho mỗi request (dùng UUID)
    request_id = str(uuid.uuid4())
    
    # order_id cho MoMo: kết hợp order ID + UUID để đảm bảo duy nhất
    # (MoMo yêu cầu orderId phải duy nhất cho mỗi giao dịch)
    momo_order_id = f"LAPSTORE_{order_id}_{uuid.uuid4().hex[:8]}"
    
    # amount phải là số nguyên (VNĐ không có phần thập phân)
    amount = int(amount)
    
    # extraData: dữ liệu bổ sung (có thể để trống)
    extra_data = ""
    
    # requestType: loại thanh toán
    # "payWithMethod" cho phép user chọn phương thức trên trang MoMo
    request_type = "payWithMethod"
    
    # ====== 3. Tạo chữ ký HMAC-SHA256 ======
    # Chuỗi raw signature theo thứ tự alphabet của key (quy định bởi MoMo)
    # QUAN TRỌNG: Thứ tự các tham số phải CHÍNH XÁC theo tài liệu MoMo
    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={amount}"
        f"&extraData={extra_data}"
        f"&ipnUrl={ipn_url}"
        f"&orderId={momo_order_id}"
        f"&orderInfo={order_info}"
        f"&partnerCode={partner_code}"
        f"&redirectUrl={redirect_url}"
        f"&requestId={request_id}"
        f"&requestType={request_type}"
    )
    
    # Tính HMAC-SHA256
    # - key: secret_key (bytes)
    # - message: raw_signature (bytes)
    # - digest: sha256
    signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # ====== 4. Tạo request body gửi tới MoMo ======
    request_body = {
        "partnerCode": partner_code,
        "accessKey": access_key,
        "requestId": request_id,
        "amount": amount,
        "orderId": momo_order_id,
        "orderInfo": order_info,
        "redirectUrl": redirect_url,
        "ipnUrl": ipn_url,
        "extraData": extra_data,
        "requestType": request_type,
        "signature": signature,
        "lang": "vi",
    }
    
    # ====== 5. Gửi POST request tới MoMo API ======
    try:
        response = requests.post(
            endpoint,
            json=request_body,
            headers={"Content-Type": "application/json"},
            timeout=30,  # Timeout 30 giây
        )
        response_data = response.json()
        
        # Thêm momo_order_id vào response để lưu lại
        response_data['momo_order_id'] = momo_order_id
        
        return response_data
        
    except requests.exceptions.RequestException as e:
        # Xử lý lỗi kết nối
        return {
            "resultCode": -1,
            "message": f"Lỗi kết nối tới MoMo: {str(e)}",
            "momo_order_id": momo_order_id,
        }


def verify_momo_signature(data):
    """
    Xác minh chữ ký từ MoMo callback (return URL hoặc IPN).
    
    Khi MoMo redirect user về hoặc gửi IPN, nó kèm theo một signature.
    Hàm này tính lại signature từ dữ liệu nhận được và so sánh
    với signature MoMo gửi về để đảm bảo dữ liệu không bị giả mạo.
    
    Args:
        data (dict): Dữ liệu từ MoMo callback (request.GET hoặc request body)
    
    Returns:
        bool: True nếu signature hợp lệ, False nếu không
    """
    secret_key = settings.MOMO_SECRET_KEY
    access_key = settings.MOMO_ACCESS_KEY
    
    # Lấy signature từ MoMo gửi về
    received_signature = data.get("signature", "")
    
    # Tính lại signature từ dữ liệu nhận được
    # Thứ tự tham số cho response signature (theo tài liệu MoMo)
    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={data.get('amount', '')}"
        f"&extraData={data.get('extraData', '')}"
        f"&message={data.get('message', '')}"
        f"&orderId={data.get('orderId', '')}"
        f"&orderInfo={data.get('orderInfo', '')}"
        f"&orderType={data.get('orderType', '')}"
        f"&partnerCode={data.get('partnerCode', '')}"
        f"&payType={data.get('payType', '')}"
        f"&requestId={data.get('requestId', '')}"
        f"&responseTime={data.get('responseTime', '')}"
        f"&resultCode={data.get('resultCode', '')}"
        f"&transId={data.get('transId', '')}"
    )
    
    # Tính HMAC-SHA256
    computed_signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # So sánh 2 signature
    return hmac.compare_digest(computed_signature, received_signature)
