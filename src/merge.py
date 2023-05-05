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
    
    async def merge_files(self, evt):
        for f in self.files:
            reader = js.FileReader.new()
            reader.onload = create_proxy(self.write_pdf)
            reader.readAsArrayBuffer(f)
        await asyncio.sleep(2)
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