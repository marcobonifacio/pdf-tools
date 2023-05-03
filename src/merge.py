import io
import js
from pyscript import Element
from pyodide.ffi.wrappers import add_event_listener, create_proxy
from pypdf import PdfReader


def show_menu():
    navbar = js.document.getElementById('top-menu')
    if navbar.className == 'menu':
        navbar.className += ' responsive'
    else:
        navbar.className = 'menu'


def modify_canvas():
    js.document.getElementById('title').style.display = 'none'
    js.document.getElementById('description').style.display = 'none'
    js.document.getElementById('select-container').style.display = 'none'
    js.document.getElementById('action-button').style.visibility = 'visible'


def read_pdf(evt):
    return PdfReader(io.BytesIO(bytes(evt.target.result.to_py())))


def select_files(evt):
    filelist = evt.target.files
    modify_canvas()
        
    for f in filelist:
        Element('target').write(f.name, append=True)
        #reader = js.FileReader.new()
        #reader.onload = create_proxy(read_pdf)
        #reader.readAsArrayBuffer(f)
    

def setup():
    add_event_listener(js.document.getElementById('selector'),
                       'change', select_files)


setup()