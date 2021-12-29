import secrets
from pprint import pprint

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/nonce', methods=('GET',))
def nonce():
    n = secrets.token_urlsafe()
    return n

@bp.route('/sign_in', methods=('POST',))
def sign_in():
    '''
    {'ens': None,
 'message': {'address': '0x464eE0FF90B7aC76d3ec8D2a25E6926DeCC88f6d',
             'chainId': '1',
             'domain': '127.0.0.1:5000',
             'issuedAt': '2021-12-29T09:36:45.039Z',
             'nonce': 'nonce',
             'signature': 'signature',
             'statement': 'EthOS',
             'type': 'Personal signature',
             'uri': 'http://127.0.0.1:5000',
             'version': '1'}}
    '''
    # pprint(request.json)
    return 'NG'