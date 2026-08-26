"""
Temporary view to update student sections. Remove after use.
"""
from django.http import JsonResponse
from django.core.management import call_command
from io import StringIO


def update_section_view(request):
    """Trigger section update."""
    secret = request.GET.get('key')
    if secret != 'attendx-seed-2024':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        out = StringIO()
        call_command('fix_cs21', stdout=out)
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
