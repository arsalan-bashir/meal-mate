from django.shortcuts import render

def desktop_only_middleware(get_response):
    def middleware(request):
        # Check the user agent for mobile or tablet
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        if "mobile" in user_agent or "tablet" in user_agent:
            return render(request, "delivery/access-denied.html", status=403)
        return get_response(request)
    return middleware