def profile_type(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'musician'):
            return {'profile_type': 'musician'}
        elif hasattr(request.user, 'band'):
            return {'profile_type': 'band'}
    return {'profile_type': None}