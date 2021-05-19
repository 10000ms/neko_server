from handler import user

user_handler = {
    '/user': user.user_index,
    '/user/login': user.user_login,
    '/user/logout': user.user_logout,
    '/user/register': user.user_register,
}
