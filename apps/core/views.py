import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def index_view(request, *args, **kwargs):
    """
    Unified Single-Page Application (SPA) entrypoint.
    Inspects incoming Host header for domain-based routing:
    - Main App (APP_URL): 'facknews.local' -> Serves public Fake News Detector & About with Contact Us.
    - Admin Portal (PORTAL_URL): 'portal.appur' ->
        If unauthenticated: Serves Login page first.
        If authenticated: Serves Admin Dashboard.
    """
    host = request.get_host().split(':')[0].lower()
    app_url = getattr(settings, 'APP_URL', 'facknews.local').lower()
    portal_url = getattr(settings, 'PORTAL_URL', 'portal.appur').lower()
    is_portal = (host == portal_url or host.startswith('portal.'))

    context = {
        'is_portal': is_portal,
        'is_authenticated': request.user.is_authenticated,
        'app_url': app_url,
        'portal_url': portal_url,
    }
    return render(request, 'index.html', context)
