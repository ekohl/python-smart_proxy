# pylint: disable=unused-argument
import ssl
from pathlib import Path

from aiohttp import ClientSession, TCPConnector
from starlette.applications import Starlette
from starlette.config import Config
from starlette.datastructures import URL
from starlette.responses import JSONResponse

app = Starlette()  # pylint: disable=invalid-name


config = Config("config/settings")  # pylint: disable=invalid-name
PUPPET_URL = config('PUPPET_URL', cast=URL)
PUPPET_CA = config('PUPPET_CA', cast=Path, default='config/puppet/ca.pem')
PUPPET_CERT = config('PUPPET_CERT', cast=Path, default='config/puppet/cert.pem')
PUPPET_KEY = config('PUPPET_KEY', cast=Path, default='config/puppet/key.pem')


def get_puppet_session(url=PUPPET_URL, cafile=PUPPET_CA, cert=PUPPET_CERT, key=PUPPET_KEY):
    ssl_ctx = ssl.create_default_context(cafile=cafile)
    ssl_ctx.load_cert_chain(cert, key)

    conn = TCPConnector(ssl_context=ssl_ctx)
    return ClientSession(connector=conn)


PUPPET_SESSION = get_puppet_session()


async def get_environments():
    url = PUPPET_URL.replace(path='/puppet/v3/environments')
    async with PUPPET_SESSION.get(str(url)) as resp:
        data = await resp.json()
    return data['environments']


async def get_classes(environment: str):
    url = PUPPET_URL.replace(path='/puppet/v3/environment_classes')
    async with PUPPET_SESSION.get(str(url), params={'environment': environment}) as resp:
        data = await resp.json()
    return data


@app.route('/features')
async def features(request):
    result = ['puppet']
    return JSONResponse(result)


@app.route('/v2/features')
async def features_v2(request):
    result = {
        'puppet': {
            'state': 'running',
            'http_enabled': True,
            'https_enabled': True,
            'capabilities': [],
            'settings': {
                'puppet_url': str(PUPPET_URL),
            },
        },
    }
    return JSONResponse(result)


@app.route('/version')
async def version(request):
    result = {
        'version': '0.1.0',
        'modules': {
            'puppet': '0.1.0',
        },
    }
    return JSONResponse(result)


@app.route('/puppet/environments')
async def environments(request):
    envs = await get_environments()
    result = list(envs.keys())
    return JSONResponse(result)


@app.route('/puppet/environments/{environment}/classes')
async def classes(request):
    data = await get_classes(request.path_params['environment'])

    result = []

    for puppet_file in data['files']:
        for cls in puppet_file['classes']:
            try:
                module, name = cls['name'].split('::', 1)
            except ValueError:
                name = cls['name']
                module = None

            params = {param['name']: param.get('default_literal', param.get('default_source'))
                      for param in cls['params']}

            result.append({
                cls['name']: {
                    'name': name,
                    'module': module,
                    'params': params,
                }
            })

    return JSONResponse(result)
