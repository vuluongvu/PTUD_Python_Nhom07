def user_profile_data(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile and profile.avatar:
            try:
                return {'user_avatar_url': profile.avatar.url}
            except:
                return {'user_avatar_url': str(profile.avatar)}
    return {'user_avatar_url': None}