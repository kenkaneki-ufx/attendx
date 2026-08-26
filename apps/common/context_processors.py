def global_context(request):
    """
    Global context processor for all templates.
    Adds common variables to all template contexts.
    """
    context = {
        'app_name': 'AttendX',
        'app_version': '1.0.0',
    }
    
    # Add user-specific context
    if request.user.is_authenticated:
        context.update({
            'user_full_name': request.user.get_full_name(),
            'is_faculty': hasattr(request.user, 'employee_id'),
            'is_admin': request.user.is_admin,
        })
    
    return context
