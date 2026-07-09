from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Middleware global : redirige vers la page de connexion si non authentifie.
    Exclut : /facial/login/, /facial/logout/, /facial/admin/, /facial/api/
    """

    EXEMPT_PREFIXES = (
        "/facial/login/",
        "/facial/logout/",
        "/facial/admin/",
        "/facial/api/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path
            if not any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
                login_url = f"/facial/login/?next={path}"
                return redirect(login_url)
        return self.get_response(request)
