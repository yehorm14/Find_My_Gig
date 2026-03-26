from gigs.models import Musician, Band

def profile_type(request):
    """
    Globally injects 'profile_type' into all templates.
    Allows navbar and base layouts to adapt based on whether 
    the user is an admin, musician, or band.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return {'profile_type': 'admin'}
        if hasattr(request.user, 'musician'):
            return {'profile_type': 'musician'}
        elif hasattr(request.user, 'band'):
            return {'profile_type': 'band'}
            
    return {'profile_type': None}

def user_profile(request):
    """
    Globally injects 'profile_pic' into all templates.
    Fetches the profile picture for the authenticated user to display 
    in headers/navbars without requiring specific view logic.
    """
    if request.user.is_authenticated:
        try:
            pic = request.user.musician.profile_picture
            return {'profile_pic': pic}
        except Musician.DoesNotExist:
            pass
            
        try:
            pic = request.user.band.profile_picture
            return {'profile_pic': pic}
        except Band.DoesNotExist:
            pass
            
    return {'profile_pic': None}