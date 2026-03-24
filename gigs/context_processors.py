def profile_type(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return {'profile_type': 'admin'}
        if hasattr(request.user, 'musician'):
            return {'profile_type': 'musician'}
        elif hasattr(request.user, 'band'):
            return {'profile_type': 'band'}
    return {'profile_type': None}