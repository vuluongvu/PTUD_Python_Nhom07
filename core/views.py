from django.shortcuts import render
import json
from .models import Product, WishList, ProductImage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
import google.generativeai as genai
import re
from functools import reduce
import operator

def home(request):

    all_new_products = Product.objects.filter(status=True).order_by('-created_at').prefetch_related('images')
    
    # mục giờ vàng
    flash_sale_laptops = all_new_products.filter(is_lap=True)[:4]
    
    # bán chạy laptop   
    bestselling_products = all_new_products.filter(is_lap=True, price__gt=20000000 )[:5]

    wishlist_ids = []
    if request.user.is_authenticated:
        
        wishlist_ids = WishList.objects.filter(user=request.user).values_list('product_id', flat=True)
    components = Product.objects.filter(Q(is_vga=True) | Q(is_cpu=True) | Q(is_ram=True))[:5]
    context = {'flash_sale_laptops': flash_sale_laptops, 'bestselling_products': bestselling_products, 'components': components, 'wishlist_ids': wishlist_ids}
    return render(request, 'core/home.html', context)

@login_required 
def wishlist_list(request):
   
    user_wishlist = WishList.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'users/wishlist.html', {
        'wishlist': user_wishlist
    })
    
def toggle_wishlist(request):
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Bạn phải đăng nhập để thêm sản phẩm vào danh sách yêu thích!'
        }, status=200)

    if request.method == "POST":
        product_id = request.POST.get('id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item = WishList.objects.filter(user=request.user, product=product)

        if wishlist_item.exists():
            wishlist_item.delete()
            status = 'removed'
            message = 'Đã xóa khỏi danh sách yêu thích.'
        else:
            WishList.objects.create(user=request.user, product=product)
            status = 'added'
            message = 'Đã thêm vào danh sách yêu thích!'
            
        # Lấy số lượng mới nhất
        wishlist_count = WishList.objects.filter(user=request.user).count()
            
        return JsonResponse({'status': status, 'message': message, 'wishlist_count': wishlist_count})
    


# xử lý api gemini
_client = None

def get_genai_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    return _client


def chatbot_api(request):
    """
    API endpoint cho chatbot, sử dụng thư viện google-genai mới.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Chỉ chấp nhận phương thức POST.'}, status=405)

    # 1. Kiểm tra API Key
    if not settings.GOOGLE_API_KEY:
        return JsonResponse({
            'reply': "Xin lỗi, dịch vụ AI chưa được cấu hình. Vui lòng liên hệ quản trị viên."
        })

    # 2. Parse JSON body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'reply': "Lỗi: Dữ liệu gửi lên không hợp lệ."}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'reply': "Vui lòng nhập câu hỏi của bạn."})

    # --- New Product Search Logic ---
    # --- Improved Product Search Logic ---
    products_found = []
    # Keywords to trigger product search. Also include common brands.
    search_trigger_keywords = ['laptop', 'máy tính', 'pc', 'linh kiện', 'cpu', 'vga', 'ram', 'giá', 'tìm', 'mua', 'sản phẩm', 'dell', 'asus', 'hp', 'lenovo', 'acer', 'msi', 'macbook']
    # Common words to ignore in the search query
    stop_words = ['cho', 'tôi', 'mua', 'bạn', 'có', 'không', 'giá', 'bao', 'nhiêu', 'tìm', 'kiếm', 'một', 'cái', 'về', 'sản', 'phẩm', 'của', 'hàng']

    user_message_lower = user_message.lower()

    if any(keyword in user_message_lower for keyword in search_trigger_keywords):
        # 1. Clean the user message to get meaningful search terms
        # Remove stop words and punctuation
        query_words = [word for word in re.split(r'\s+', user_message_lower) if word not in stop_words]
        cleaned_query = ' '.join(re.sub(r'[^\w\s]', '', word) for word in query_words)
        search_terms = [term for term in cleaned_query.split() if term]

        if search_terms:
            # 2. Build a dynamic query to match ALL terms (more precise)
            try:
                strict_query = reduce(operator.and_, (Q(name__icontains=term) for term in search_terms))
                products = Product.objects.filter(strict_query, status=True).distinct().prefetch_related('images')[:3]

                # 3. If no results, try a more lenient search matching ANY term
                if not products.exists():
                    lenient_query = reduce(operator.or_, (Q(name__icontains=term) for term in search_terms))
                    products = Product.objects.filter(lenient_query, status=True).distinct().prefetch_related('images')[:3]

                for p in products:
                    products_found.append({
                        'name': p.name,
                        'url': reverse('products:product-detail', args=[p.slug]),
                        'price': p.price_vn,
                        'image_url': p.images.first().image_url if p.images.first() else None,
                    })
            except Exception as e:
                # Catch potential errors if search_terms is empty after cleaning
                print(f"Error during product search: {e}")

    # 3. Gọi Gemini API
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)

        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=(
                "Bạn là một trợ lý ảo thân thiện và chuyên nghiệp của LapStore, "
                "một cửa hàng chuyên bán laptop và linh kiện máy tính. "
                "Hãy trả lời các câu hỏi của khách hàng một cách ngắn gọn, rõ ràng, "
                "tập trung vào các sản phẩm và dịch vụ của cửa hàng. "
                "Từ chối lịch sự nếu câu hỏi không liên quan đến mua sắm tại LapStore."
            )
        )

        generation_config = {
            "max_output_tokens": 512,
            "temperature": 0.7,
        }

        response = model.generate_content(
            user_message,
            generation_config=generation_config
        )

        # Kiểm tra response hợp lệ trước khi lấy .text
        if response and response.text:
            bot_reply = response.text
        else:
            bot_reply = "Xin lỗi, mình không có câu trả lời phù hợp lúc này."

    except Exception as e:
        error_str = str(e)
        print(f"[Gemini API Error] {type(e).__name__}: {e}")

        #  Xử lý từng loại lỗi cụ thể
        if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
            bot_reply = "Chatbot đang quá tải, vui lòng thử lại sau ít phút nhé! 🙏"
        elif '404' in error_str or 'NOT_FOUND' in error_str:
            bot_reply = "Xin lỗi, dịch vụ AI tạm thời không khả dụng. Vui lòng thử lại sau."
        elif '401' in error_str or 'UNAUTHENTICATED' in error_str:
            bot_reply = "Lỗi xác thực API. Vui lòng liên hệ quản trị viên."
        else:
            bot_reply = "Xin lỗi, hệ thống AI đang gặp sự cố. Vui lòng thử lại sau."

    # 4. Construct final response
    response_data = {
        'reply': bot_reply,
        'products': products_found # Add the list of products
    }
    return JsonResponse(response_data)