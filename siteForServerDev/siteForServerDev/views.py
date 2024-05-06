from django.shortcuts import render
from django.http import HttpResponseForbidden

from authorizationModule.functions import check_token, decode_token
from authorizationModule.models import UserTokens, Roles, UserRoles, MethodsLog


def home(request):
    user_tokens = 0
    token_data = decode_token(request.COOKIES.get('jwt_token'))
    if token_data != 'Error':
        MethodsLog.add_log_record_by_user_id('home', token_data.get('id'))
        user_tokens = UserTokens.all_user_tokens(token_data.get('id'))
    return render(request, "siteForServerDev/home.html", {'token_data': token_data, 'user_tokens':user_tokens})

def role_test(request):
    roles = Roles.objects.all()
    user_roles = UserRoles.objects.all()
    token = request.COOKIES.get('jwt_token')
    check = check_token(request)
    token_data = decode_token(token)
    if token_data != 'Error':
        MethodsLog.add_log_record_by_user_id('roleTest', token_data.get('id'))
        if check != 'Error':
            all_user_roles = UserRoles.get_all_user_roles_by_id(token_data.get('id'))
            if token_data.get('is_staff') or token_data.get('crud', {}).get('/roletest', {}).get('read_p'):
                return render(request, "siteForServerDev/roletest.html", {'token_data': token_data, 'all_user_roles': all_user_roles, 'roles': roles, 'user_roles': user_roles})
    return HttpResponseForbidden()
