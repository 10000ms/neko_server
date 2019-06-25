# -*- coding: utf-8 -*-

setting = dict(
    host='127.0.0.1',
    port=9655,

    # RFC 2616
    standard_format='iso-8859-1',

    http_state={
        200: 'ok',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        500: 'Internal Server Error',
    }
)
