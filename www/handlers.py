import re, time, json, logging, hashlib, base64, asyncio, apis, config

from coroweb import get, post

from aiohttp import web

from Models import User, Comment, Blog, next_id


@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


# @get('/')
# def index(request):
#     summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
#     blogs = [
#         Blog(id='1', name='Test Blog', summary=summary, create_at=time.time()-120),
#         Blog(id='2', name='Something New', summary=summary, create_at=time.time()-3600),
#         Blog(id='3', name='Learn Swift', summary=summary, create_at=time.time()-7200)
#     ]
#     return {
#         '__template__': 'blogs.html',
#         'blogs': blogs,
#         '__user__': request.__user__
#     }


@get('/api/users')
async def api_get_users():
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)


#显示注册页面
@get('/register')#这个作用是用来显示登录页面
def register():
    return {
        '__template__': 'register.html'
    }


#制作cookie的数值，即set_cookie的value
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1（id-到期时间-摘要算法）
    expires = str(time.time()+max_age)
    s = '%s-%s-%s-%s'%(user.id, user.passwd, expires, _COOKIE_KEY)#s的组成：id, passwd, expires, _COOKIE_KEY
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]#再把s进行摘要算法
    return '-'.join(L)


COOKIE_NAME = 'awesession'#用来在set_cookie中命名
_COOKIE_KEY = config.configs['session']['secret']#导入默认设置


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise apis.APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise apis.APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise apis.APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise apis.APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

COOKIE_NAME = 'awesession'#用来在set_cookie中命名
_COOKIE_KEY = config.configs['session']['secret']#导入默认设置


#验证登录信息
@post('/api/authenticate')
async def authenticate(*,email,passwd):
    if not email:
        raise apis.APIValueError('email')
    if not passwd:
        raise apis.APIValueError('passwd')
    users = await User.findall(where='email=?',args=[email])
    if len(users) == 0:
        raise apis.APIValueError('email','Email not exist.')
    user = users[0]#此时finall得出来的数值是一个仅含一个dict的list,就是sql语句返回什么类型的数据自己忘了
    #把登录密码转化格式并进行摘要算法
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if sha1.hexdigest() != user.passwd:#与数据库密码比较
        raise apis.APIValueError('password','Invaild password')
    #制作cookie发送给浏览器，这步骤与注册用户一样
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400), max_age=86400, httponly=True)
    user.passwd = "******"
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
    return r


async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-') #拆分字符串(D)
        if len(L) !=3:
            return None
        uid, expires, sha1 = L
        if float(expires) < time.time():#查看是否过期,这里廖大用的是int，但是字符串用int的时候，只能全是数字，不能含小数点
            return None
        user = await User.find(uid)
        if not user:
            return None
        #用数据库来生字符串(C)与cookie的比较
        s = '%s-%s-%s-%s'%(uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = "******"
        return user
    except Exception as e:
        logging.exception(e)
        return None


