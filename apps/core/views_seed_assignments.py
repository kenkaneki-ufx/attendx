from django.http import JsonResponse
from django.core.management import call_command
from io import StringIO


def seedfacultyassignments_view(request):
    """Temporary view to seed faculty assignments."""
    # Security check
    key = request.GET.get('key')
    if key != 'attendx-seed-2024':
        return JsonResponse({'error': 'Invalid key'}, status=403)
    
    try:
        output = StringIO()
        call_command('seedfacultyassignments', stdout=output)
        output_text = output.getvalue()
        return JsonResponse({
            'success': True,
            'output': output_text
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
