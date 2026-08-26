"""
Temporary view to seed AKTU data. Remove after use.
"""
from django.http import JsonResponse
from django.conf import settings
from django.core.management import call_command
from io import StringIO


def seedaktu_view(request):
    """Trigger AKTU data seeding. Only works with secret key."""
    # Security: only allow with correct key
    secret = request.GET.get('key')
    if secret != 'attendx-seed-2024':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        out = StringIO()
        call_command('seedaktu', stdout=out)
        output = out.getvalue()
        return JsonResponse({
            'success': True,
            'output': output
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
