import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post

from Models import User, Comment, Blog, next_id

@get('/')
async def index(request):
##    users = await User.findAll()
    users = [1, ]
    return {
        '__template__': 'test.html',
        'users': users
    }