import os
import js
from pyodide.ffi.wrappers import add_event_listener, create_proxy
from pypdf import PdfReader

def show_menu():
    navbar = js.document.getElementById('top-menu')
    if navbar.className == 'menu':
        navbar.className += ' responsive'
    else:
        navbar.className = 'menu'

def read_pdf(evt):
    with open('tmp', 'w') as f:
        f.write(evt.target.result)
    pdf = PdfReader('tmp')
    os.remove('tmp')
    js.console.log(len(pdf.pages))

def select_pdf(evt):
    filelist = evt.target.files
    for f in filelist:
        reader = js.FileReader.new()
        reader.onload = create_proxy(read_pdf)
        reader.readAsBinaryString(f)

add_event_listener(js.document.getElementById('selector'), 'change', 
                   select_pdf)