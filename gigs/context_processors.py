def profile_type(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return {'profile_type': 'admin'}
        if hasattr(request.user, 'musician'):
            return {'profile_type': 'musician'}
        elif hasattr(request.user, 'band'):
            return {'profile_type': 'band'}
    return {'profile_type': None}

def user_profile(request):
    if request.user.is_authenticated:
        try:
            pic = request.user.musician.profile_picture
            return {'profile_pic': pic}
        except:
            pass
        try:
            pic = request.user.band.profile_picture
            return {'profile_pic': pic}
        except:
            pass
    return {'profile_pic': None}