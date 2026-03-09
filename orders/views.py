import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from core.views import toggle_wishlist
from core.models import Product, WishList, Cart, Order, OrderItem, Coupon, Payment
from django.contrib import messages
from django.utils import timezone

from orders.services.momo_service import create_momo_payment, verify_momo_signature

logger = logging.getLogger(__name__)

app_name = 'orders'

# Create your views here.

# -------------------view cart----------------------- 
def view_cart(request):
    # Nếu người dùng chưa đăng nhập, hiển thị trang giỏ hàng trống
    if not request.user.is_authenticated:
        return render(request, 'orders/cart.html', {
            'cart_items': [],
            'product_count': 0,
            'needs_login': True
        })

    # Lấy giỏ hàng của người dùng. Nếu không có, tạo một giỏ hàng trống.
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Lấy tất cả các sản phẩm (CartItem) trong giỏ hàng đó
    cart_items = user_cart.items.select_related('product').prefetch_related('product__images').all()
    
    # Tính tổng tiền ban đầu
    total_amount = sum(item.product.final_price * item.quantity for item in cart_items)

    # --- Logic xử lý Coupon ---
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            # Kiểm tra lại coupon với giỏ hàng hiện tại
            if coupon.status and coupon.expired_date >= timezone.now() and total_amount >= coupon.min_order_value:
                discount_amount = coupon.discount_value
            else: # Coupon không còn hợp lệ
                del request.session['coupon_id']
                coupon = None
        except Coupon.DoesNotExist:
            del request.session['coupon_id']

    final_total = total_amount - discount_amount

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'product_count': cart_items.count(),
        'total_amount': total_amount,
        'coupon': coupon,
        'discount_amount': discount_amount,
        'final_total': final_total,
    })

# -------------------checkout--------------------------- 
@login_required
def checkout(request):
    """View for the checkout page."""
    try:
        user_cart = Cart.objects.get(user=request.user)
        cart_items = user_cart.items.select_related('product').prefetch_related('product__images').all()
        if not cart_items:
            # Nếu giỏ hàng trống, không cho vào checkout
            return redirect('orders:cart')
    except Cart.DoesNotExist:
        # Nếu không có giỏ hàng, cũng không cho vào
        return redirect('orders:cart')

    # --- Logic tính toán tổng tiền và Coupon ---
    total_amount = sum(item.product.final_price * item.quantity for item in cart_items)
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            # Kiểm tra lại coupon
            if coupon.status and coupon.expired_date >= timezone.now() and total_amount >= coupon.min_order_value:
                discount_amount = coupon.discount_value
            else: # Coupon không hợp lệ, xóa khỏi session
                del request.session['coupon_id']
                coupon = None
        except Coupon.DoesNotExist:
            del request.session['coupon_id']
    final_total = total_amount - discount_amount

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        shipping_name = request.POST.get('fullname')
        shipping_phone = request.POST.get('phone')
        street_address = request.POST.get('address')
        ward_text = request.POST.get('ward_text')
        district_text = request.POST.get('district_text')
        province_text = request.POST.get('province_text')
        payment_method = request.POST.get('payment')

        # Ghép các thành phần địa chỉ lại
        address_parts = [part for part in [street_address, ward_text, district_text, province_text] if part]
        full_address = ", ".join(address_parts)

        # Tạo đơn hàng
        new_order = Order.objects.create(
            user=request.user,
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=full_address,
            coupon=coupon, # Gán coupon vào đơn hàng
            total_amount=final_total # Sử dụng tổng tiền cuối cùng
        )

        # Chuyển các sản phẩm từ giỏ hàng sang chi tiết đơn hàng
        for item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=(item.product.final_price or 0)
            )

        # Giảm số lượng coupon nếu có
        if coupon:
            coupon.quantity -= 1
            coupon.save()

        # Xóa giỏ hàng và coupon trong session sau khi đã đặt hàng thành công
        user_cart.delete()
        if 'coupon_id' in request.session:
            del request.session['coupon_id']

        # ===== XỬ LÝ THANH TOÁN MOMO =====
        if payment_method == 'momo':
            # Tạo Payment record với trạng thái chờ thanh toán
            payment = Payment.objects.create(
                order=new_order,
                payment_method=Payment.Method.MOMO,
                payment_status=Payment.Status.PENDING,
            )

            # Gọi MoMo API để tạo yêu cầu thanh toán
            order_info = f"LapStore - Thanh toán đơn hàng #{new_order.id}"
            momo_response = create_momo_payment(
                order_id=new_order.id,
                amount=final_total,
                order_info=order_info,
            )

            # Kiểm tra kết quả từ MoMo
            if momo_response.get('resultCode') == 0 and momo_response.get('payUrl'):
                # Lưu momo_order_id vào transaction_id để tra cứu sau
                payment.transaction_id = momo_response.get('momo_order_id', '')
                payment.save()

                # Redirect user tới trang thanh toán MoMo
                return redirect(momo_response['payUrl'])
            else:
                # MoMo trả lỗi → đánh dấu payment thất bại
                payment.payment_status = Payment.Status.FAILED
                payment.save()
                error_msg = momo_response.get('message', 'Không thể tạo thanh toán MoMo')
                logger.error(f"MoMo payment creation failed for order #{new_order.id}: {error_msg}")
                messages.error(request, f"Lỗi thanh toán MoMo: {error_msg}. Đơn hàng đã được tạo, bạn có thể thử lại.")
                return redirect('users:order_list')

        # ===== XỬ LÝ COD / BANKING (giữ nguyên logic cũ) =====
        else:
            # Tạo Payment record cho COD/Banking
            pm_method = Payment.Method.COD  # Mặc định
            if payment_method == 'banking':
                pm_method = Payment.Method.BANKING
            
            Payment.objects.create(
                order=new_order,
                payment_method=pm_method,
                payment_status=Payment.Status.PENDING,
            )
            messages.success(request, "Đặt hàng thành công! Cảm ơn bạn đã mua sắm tại LapStore.")
            return redirect('users:order_list')

    # --- Context cho GET request ---
    context = {
        'cart_items': cart_items,
        'product_count': cart_items.count(),
        'total_amount': total_amount,
        'coupon': coupon,
        'discount_amount': discount_amount,
        'final_total': final_total,
    }
    return render(request, 'orders/checkout.html', context)


# -------------------coupon views-----------------------
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        now = timezone.now()

        try:
            # Step 1: Find coupon by code first for better error messages.
            coupon = Coupon.objects.get(code__iexact=code)

            # Step 2: Check other conditions and provide specific feedback.
            if not coupon.status:
                return JsonResponse({'status': 'error', 'message': 'Mã giảm giá này đã bị vô hiệu hóa.'})
            if coupon.expired_date < now:
                return JsonResponse({'status': 'error', 'message': 'Mã giảm giá này đã hết hạn.'})
            if coupon.quantity <= 0:
                return JsonResponse({'status': 'error', 'message': 'Mã giảm giá này đã hết lượt sử dụng.'})

            # Step 3: Check against the cart.
            user_cart = Cart.objects.get(user=request.user)
            cart_items = user_cart.items.select_related('product').all()
            total_amount = sum(item.product.final_price * item.quantity for item in cart_items)

            if total_amount < coupon.min_order_value:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Mã này chỉ áp dụng cho đơn hàng từ {int(coupon.min_order_value):,}đ.'
                })

            # --- Success ---
            request.session['coupon_id'] = coupon.id

            discount_amount = coupon.discount_value
            final_total = total_amount - discount_amount

            return JsonResponse({
                'status': 'success',
                'message': 'Áp dụng mã giảm giá thành công!',
                'coupon_code': coupon.code,
                'discount_amount': discount_amount,
                'new_total': final_total,
            })

        except Coupon.DoesNotExist:
            # This now only triggers if the code itself does not exist.
            return JsonResponse({'status': 'error', 'message': 'Mã giảm giá không tồn tại.'})
        except Cart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Giỏ hàng của bạn trống.'})

    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

@login_required
def remove_coupon(request):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.success(request, "Đã xóa mã giảm giá.")
    # Chuyển hướng về trang người dùng vừa thao tác, mặc định là giỏ hàng
    redirect_url = request.META.get('HTTP_REFERER', 'orders:cart')
    return redirect(redirect_url)

# -------------------view wishlist----------------------- 
def wishlist_list(request):
    if not request.user.is_authenticated:
        # Nếu chưa login, vẫn cho vào trang nhưng wishlist sẽ trống
        return render(request, 'orders/wishlist.html', {
            'wishlist': [],
            'needs_login': True # Gửi thêm biến này để template xử lý
        })
    
    user_wishlist = WishList.objects.filter(user=request.user).select_related('product')
    product_count = user_wishlist.count()
    return render(request, 'orders/wishlist.html', {
        'wishlist': user_wishlist, 
        'product_count': product_count,
        })


# ==================== MOMO PAYMENT VIEWS ====================

def momo_return(request):
    """
    Xử lý khi MoMo redirect user về sau khi thanh toán.
    
    MoMo gửi kết quả thanh toán qua query parameters (GET request).
    View này xác minh chữ ký và hiển thị kết quả cho user.
    
    Luồng:
    1. User hoàn tất (hoặc hủy) thanh toán trên trang MoMo
    2. MoMo redirect user về URL này kèm theo các query params
    3. Ta xác minh chữ ký (signature) để đảm bảo dữ liệu hợp lệ
    4. Cập nhật trạng thái Payment và hiển thị kết quả
    """
    # Lấy dữ liệu từ query parameters
    data = request.GET.dict()
    
    result_code = data.get('resultCode', '')
    momo_order_id = data.get('orderId', '')
    amount = data.get('amount', 0)
    message = data.get('message', '')
    trans_id = data.get('transId', '')
    
    # Trích xuất order_id từ momo_order_id (format: LAPSTORE_{order_id}_{uuid})
    order_id = None
    try:
        parts = momo_order_id.split('_')
        if len(parts) >= 2:
            order_id = int(parts[1])
    except (ValueError, IndexError):
        pass
    
    # Xác minh chữ ký từ MoMo
    is_valid_signature = verify_momo_signature(data)
    
    # Kiểm tra kết quả: resultCode == 0 là thành công
    success = (str(result_code) == '0') and is_valid_signature
    
    # Cập nhật trạng thái Payment trong database
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            if success:
                payment.payment_status = Payment.Status.COMPLETED
                payment.transaction_id = trans_id or momo_order_id
                payment.save()
                
                # Cập nhật trạng thái đơn hàng
                order = payment.order
                order.order_status = Order.Status.PROCESSING
                order.save()
            else:
                payment.payment_status = Payment.Status.FAILED
                payment.save()
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for order_id={order_id}")
    
    # Render trang kết quả
    context = {
        'success': success,
        'order_id': order_id,
        'momo_order_id': momo_order_id,
        'amount': int(amount) if amount else 0,
        'message': message,
    }
    return render(request, 'orders/momo_result.html', context)


@csrf_exempt  # MoMo gửi POST request từ server, không có CSRF token
def momo_ipn(request):
    """
    Xử lý IPN (Instant Payment Notification) từ MoMo.
    
    Đây là callback server-to-server: MoMo gửi POST request tới URL này
    để thông báo kết quả thanh toán, KHÔNG phụ thuộc vào redirect của user.
    
    Tại sao cần IPN?
    - User có thể đóng trình duyệt trước khi redirect về
    - Đảm bảo cập nhật trạng thái thanh toán một cách đáng tin cậy
    
    Lưu ý: Trên localhost, MoMo KHÔNG GỬI ĐƯỢC IPN vì URL không public.
    Để test IPN, cần dùng ngrok hoặc deploy lên server.
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
    try:
        # Parse JSON body từ MoMo
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    
    logger.info(f"MoMo IPN received: {data}")
    
    # Xác minh chữ ký
    if not verify_momo_signature(data):
        logger.warning("MoMo IPN: Invalid signature")
        return JsonResponse({'message': 'Invalid signature'}, status=400)
    
    result_code = data.get('resultCode', '')
    momo_order_id = data.get('orderId', '')
    trans_id = data.get('transId', '')
    
    # Trích xuất order_id
    order_id = None
    try:
        parts = momo_order_id.split('_')
        if len(parts) >= 2:
            order_id = int(parts[1])
    except (ValueError, IndexError):
        pass
    
    if not order_id:
        return JsonResponse({'message': 'Invalid orderId'}, status=400)
    
    # Cập nhật trạng thái Payment
    try:
        payment = Payment.objects.get(order_id=order_id)
        
        if str(result_code) == '0':  # Thanh toán thành công
            payment.payment_status = Payment.Status.COMPLETED
            payment.transaction_id = trans_id or momo_order_id
            payment.save()
            
            # Cập nhật trạng thái đơn hàng sang "Đang xử lý"
            order = payment.order
            order.order_status = Order.Status.PROCESSING
            order.save()
            
            logger.info(f"MoMo IPN: Payment completed for order #{order_id}")
        else:  # Thanh toán thất bại
            payment.payment_status = Payment.Status.FAILED
            payment.save()
            logger.info(f"MoMo IPN: Payment failed for order #{order_id}, resultCode={result_code}")
    
    except Payment.DoesNotExist:
        logger.warning(f"MoMo IPN: Payment not found for order_id={order_id}")
        return JsonResponse({'message': 'Payment not found'}, status=404)
    
    # Trả về 204 No Content để MoMo biết đã nhận được IPN
    return JsonResponse({'message': 'OK'}, status=200)
