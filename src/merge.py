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


def modify_canvas():
    js.document.getElementById('title').style.display = 'none'
    js.document.getElementById('description').style.display = 'none'
    js.document.getElementById('select-container').style.display = 'none'
    js.document.getElementById('action-button').style.visibility = 'visible'
    js.document.getElementById('add-container').style.visibility = 'visible'
    add_event_listener(js.document.getElementById('add-selector'),
                       'change', pdf_merge.select_files)
    add_event_listener(js.document.getElementById('action-button'),
                       'click', pdf_merge.merge_files)


def modify_canvas_again():
    for child in js.document.getElementById('target').children:
        child.style.display = 'none'
    js.document.getElementById('add-container').style.display = 'none'
    js.document.getElementById('action-button').style.display = 'none'
    p = js.document.createElement('p')
    p.innerHTML = 'Your PDF file is ready to download!'
    js.document.getElementById('target').appendChild(p)
    link = js.document.createElement('a')
    link.innerHTML = 'Download PDF'
    link.classList.add('merge')
    js.document.getElementById('target').appendChild(link)


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
            Element('target').write(f.name, append=True)
    
    def read_files(self):
        for f in self.files:
            reader = js.FileReader.new()
            reader.onload = create_proxy(self.write_pdf)
            reader.readAsArrayBuffer(f)
    
    def merge_files(self, evt):
        self.read_files()
        modify_canvas_again()
    
    def remainder(self):
        output = io.BytesIO()
        self.merger.write(output)
        self.merger.close()
        output.seek(0)
        content = to_js(output.read())
        blob = js.Blob.new([content], {type: "application/pdf"})
        blob_url = js.window.URL.createObjectURL(blob)
        templink = js.document.createElement('a')
        templink.style.display = 'none'
        templink.href = blob_url
        templink.setAttribute('download', 'merged_pdf.pdf')
        js.document.body.appendChild(templink)
        templink.click()
        js.document.body.removeChild(templink)
        js.window.URL.revokeObjectURL(blob_url)
    

def setup():
    add_event_listener(js.document.getElementById('selector'),
                       'change', pdf_merge.select_files)


pdf_merge = PdfMerge()
setup()