import asyncio
import io
import js
from pyscript import Element
from pyodide.ffi import to_js
from pyodide.ffi.wrappers import add_event_listener, create_proxy
from pypdf import PdfWriter


def show_menu():
    navbar = js.document.getElementById('top-menu')
    if navbar.className == 'menu':
        navbar.className += ' responsive'
    else:
        navbar.className = 'menu'


def drag_enter(evt):
    evt.preventDefault()
    js.document.getElementById('div-drag').style.display = 'flex'


def drag_over(evt):
    evt.preventDefault()
    if js.document.getElementById('div-drag').style.display == 'none':
        js.document.getElementById('div-drag').style.display = 'flex'


def drag_leave(evt):
    evt.preventDefault()
    js.document.getElementById('div-drag').style.display = 'none'


def show_tooltip(evt):
    tt = js.document.createElement('div')
    tt.id = 'tooltip'
    tt.style.position = 'absolute'
    tt.style.top = f'{evt.pageY}px'
    tt.style.left = f'{evt.pageX}px'
    tt.innerHTML = evt.target.innerHTML
    js.document.body.appendChild(tt)


def hide_tooltip(evt):
    tt = js.document.getElementById('tooltip')
    js.document.body.removeChild(tt)


def modify_canvas():
    js.document.getElementById('title').style.display = 'none'
    js.document.getElementById('description').style.display = 'none'
    js.document.getElementById('dragndrop').style.display = 'none'
    js.document.getElementById('select-container').style.display = 'none'
    js.document.getElementById('action-button').style.visibility = 'visible'
    js.document.getElementById('add-container').style.visibility = 'visible'
    js.document.getElementById('target').classList.add('files')
    add_event_listener(js.document.getElementById('add-selector'),
                       'change', pdf_merge.select_files)
    add_event_listener(js.document.getElementById('action-button'),
                       'click', pdf_merge.merge_files)


def modify_canvas_again():
    for child in js.document.getElementById('target').children:
        child.style.display = 'none'
    js.document.getElementById('add-container').style.display = 'none'
    js.document.getElementById('action-button').style.display = 'none'
    js.document.getElementById('target').classList.remove('files')
    p = js.document.createElement('p')
    p.innerHTML = 'Your PDF file is ready to download!'
    js.document.getElementById('target').appendChild(p)
    link = js.document.createElement('a')
    link.id = 'pdf-download'
    link.innerHTML = 'Download PDF'
    link.classList.add('merge')
    link.setAttribute('download', 'merged_pdf.pdf')
    js.document.getElementById('target').appendChild(link)
    add_event_listener(js.document.getElementById('pdf-download'),
                       'click', pdf_merge.download_merged)


class PdfMerge:

    def __init__(self):
        self.files = []
        self.merger = PdfWriter()
    
    def write_pdf(self, evt):
        self.merger.append(io.BytesIO(bytes(evt.target.result.to_py())))
        
    def select_files(self, evt):
        if evt.target.id == 'selector':
            modify_canvas()
        filelist = evt.target.files
        for f in filelist:
            self.files.append(f)
            el = js.document.createElement('div')
            el.innerHTML = f.name
            el.classList.add('pdf')
            js.document.getElementById('target').appendChild(el)
            add_event_listener(el, 'mouseenter', show_tooltip)
            add_event_listener(el, 'mouseleave', hide_tooltip)
        evt.target.value = ''
        if len(self.files) < 2:
            (js.document.getElementById('action-button').
             setAttribute('disabled', True))
        else:
            (js.document.getElementById('action-button').
             removeAttribute('disabled'))
    
    def drop_files(self, evt):
        js.document.getElementById('div-drag').style.display = 'none'
        evt.preventDefault()
        if len(self.files) == 0:
            modify_canvas()
        for i in evt.dataTransfer.items:
            if i.kind == 'file':
                f = i.getAsFile()
                self.files.append(f)
                el = js.document.createElement('div')
                el.innerHTML = f.name
                el.classList.add('pdf')
                js.document.getElementById('target').appendChild(el)
        if len(self.files) < 2:
            (js.document.getElementById('action-button').
             setAttribute('disabled', True))
        else:
            (js.document.getElementById('action-button').
             removeAttribute('disabled'))
    
    def read_files(self):
        for f in self.files:
            reader = js.FileReader.new()
            reader.onload = create_proxy(self.write_pdf)
            reader.readAsArrayBuffer(f)
    
    def merge_files(self, evt):
        self.read_files()
        modify_canvas_again()
    
    def download_merged(self, evt):
        output = io.BytesIO()
        self.merger.write(output)
        self.merger.close()
        output.seek(0)
        content = to_js(output.read())
        blob = js.Blob.new([content], {type: "application/pdf"})
        blob_url = js.window.URL.createObjectURL(blob)
        link = js.document.getElementById('pdf-download')
        link.href = blob_url
    

def setup():
    add_event_listener(js.document.getElementById('selector'),
                       'change', pdf_merge.select_files)
    add_event_listener(js.document.getElementById('target'),
                       'dragenter', drag_enter)
    add_event_listener(js.document.getElementById('div-drag'),
                       'dragover', drag_over)
    add_event_listener(js.document.getElementById('div-drag'),
                       'dragleave', drag_leave)
    add_event_listener(js.document.getElementById('div-drag'),
                       'drop', pdf_merge.drop_files)


pdf_merge = PdfMerge()
setup()