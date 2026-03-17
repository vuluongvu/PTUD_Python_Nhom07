import logging

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_order_invoice_email(order):
    """
    Gửi email hóa đơn đến khách hàng sau khi đặt hàng thành công.

    Args:
        order: Order instance (cần có related items và user).

    Returns:
        True nếu gửi thành công, False nếu thất bại.
    """
    try:
        # Lấy email người nhận: ưu tiên email nhập trong form checkout
        user = order.user
        recipient_email = order.shipping_email or (user.email if user else None)
        if not recipient_email:
            logger.warning(
                f"Order #{order.id}: Không thể gửi email — không có email người nhận."
            )
            return False

        # Lấy danh sách sản phẩm trong đơn hàng
        order_items = order.items.all()

        # Chuẩn bị context cho template
        context = {
            'customer_name': order.shipping_name or user.get_full_name() or user.username,
            'order_id': order.id,
            'order_date': order.created_at or timezone.now(),
            'order_items': order_items,
            'total_amount': order.total_amount,
        }

        # Render HTML template
        html_content = render_to_string(
            'orders/email/invoice.html', context
        )

        # Tạo và gửi email
        subject = f'LapStore — Xác nhận đơn hàng #{order.id}'
        email = EmailMessage(
            subject=subject,
            body=html_content,
            to=[recipient_email],
        )
        email.content_subtype = 'html'  # Gửi dưới dạng HTML
        email.send(fail_silently=False)

        logger.info(f"Order #{order.id}: Invoice email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(
            f"Order #{order.id}: Gửi email thất bại — {e}",
            exc_info=True,
        )
        return False
