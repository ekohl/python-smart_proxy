# pylint: disable=unused-argument
from starlette.applications import Starlette
from starlette.responses import JSONResponse


app = Starlette()  # pylint: disable=invalid-name


@app.route('/features')
async def features(request):
    result = ['puppet']
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
    result = ['production']
    return JSONResponse(result)


@app.route('/puppet/environments/{environment}/classes')
async def classes(request):
    result = [
        {
            'ntp': {
                'name': 'ntp',
                'module': None,
                'params': {
                    'server': 'ntp.example.com',
                },
            },
        },
    ]
    return JSONResponse(result)
