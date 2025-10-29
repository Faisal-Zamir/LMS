from courses.views import get_cart_items

def cart_subtotal(request):
    cart_items, _, _ = get_cart_items(request)
    if cart_items:
        subtotal = sum(course.offer_price for course in cart_items)
    else:
        subtotal = 0
    return {'subtotal': subtotal}
