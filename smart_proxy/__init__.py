# pylint: disable=unused-argument
from starlette.applications import Starlette
from starlette.responses import JSONResponse


app = Starlette()  # pylint: disable=invalid-name


@app.route('/features')
async def features(request):
    result = []
    return JSONResponse(result)
