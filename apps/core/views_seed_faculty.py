"""
Temporary view to seed faculty accounts. Remove after use.
"""
from django.http import JsonResponse
from django.core.management import call_command
from io import StringIO


def seedfaculty_view(request):
    """Trigger faculty seeding."""
    secret = request.GET.get('key')
    if secret != 'attendx-seed-2024':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        out = StringIO()
        call_command('seedfaculty', stdout=out)
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
