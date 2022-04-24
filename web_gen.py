try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from microdot_asyncio import Microdot, Response
from machine import Pin
from neo_patterns import *

app = Microdot()

@app.route('/')
@app.route('/command')
async def hello(request):
    return Response.send_file('index.html', status_code=200)

@app.route('/docs')
async def show_docs(request):
    return Response.send_file('docs.html', status_code=200)

@app.route('/json_config')
async def get_config(request):
    return Response.send_file('config.json', status_code=200)

@app.route('/button_config')
async def get_button_config(request):
    return Response.send_file('buttons.json', status_code=200)

@app.route('/config_send')
async def show_config_req(request):
    print("CONFIG DATA - REQ QUERY: {}".format(request.query_string))
    save_config(request.query_string)
    return Response.send_file('config.html', status_code=200)

@app.route('/queue/<job>')
async def get_queue(request,job):
    messages.append(job)
    return Response.redirect('/', status_code=302)

@app.route('/cmd/<job>')
async def get_cmd(request,job):
    messages.append(job)
    return Response(body="['Queued']", status_code=200)

@app.route('/scene/<job>')
async def get_scene(request,job):
    scene_def = "{}:{}".format(job,request.query_string)
    messages.append(scene_def)
    return Response.redirect('/', status_code=302)

@app.route('/<path>')
async def serve_path(request,path):
    try:
        return Response.send_file(path, status_code=200)
    except:
        print ("Request for {} NOT FOUND".format(path))
        return 'Request for {} NOT FOUND'.format(path)

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'
