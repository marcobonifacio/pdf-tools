import asyncio
import io
import js
from pyscript import Element
from pyodide.ffi import to_js
from pyodide.ffi.wrappers import add_event_listener, create_proxy
from pypdf import PdfWriter


def vw2px(vw):
    return vw * js.window.innerWidth / 100


def vh2px(vh):
    return vh * js.window.innerHeight / 100


def px2vw(px):
    return px * 100 / js.window.innerWidth


def px2vh(px):
    return px * 100 / js.window.innerHeight


def order_x(x):
    return (round(px2vh(x)) - 6) / 17


def order_y(x, offset):
    return (round(px2vh(x)) - offset) / 22


def order(x, y, offset):
    return 3 * order_x(x) + order_y(y, offset)


def show_menu():
    navbar = js.document.getElementById('top-menu')
    if navbar.className == 'menu':
        navbar.className += ' responsive'
    else:
        navbar.className = 'menu'


def drag_enter(evt):
    evt.preventDefault()
    if 'Files' in evt.dataTransfer.types:
        js.document.getElementById('div-drag').style.display = 'flex'


def drag_over(evt):
    evt.preventDefault()
    if ('Files' in evt.dataTransfer.types and 
        js.document.getElementById('div-drag').style.display == 'none'):
        js.document.getElementById('div-drag').style.display = 'flex'


def drag_end(evt):
    evt.target.classList.remove('draggable')


def drag_leave(evt):
    evt.preventDefault()
    js.document.getElementById('div-drag').style.display = 'none'


def show_tooltip(evt):
    coords = evt.target.getBoundingClientRect()
    x = coords.left + vw2px(3)
    y = coords.top + vh2px(4)
    tt = js.document.createElement('div')
    tt.id = 'tooltip'
    tt.classList.add('tooltip')
    tt.style.top = f'{y}px'
    tt.style.left = f'{x}px'
    tt.innerHTML = evt.target.innerHTML.split('<p style="')[0]
    js.document.body.appendChild(tt)


def hide_tooltip(evt):
    tt = js.document.getElementById('tooltip')
    if tt in js.document.body.children:
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


def enter_div(evt):
    evt.preventDefault()
    for c in evt.target.children:
        c.style.visibility = 'visible'


def leave_div(evt):
    evt.preventDefault()
    for c in evt.target.children:
        c.style.visibility = 'hidden'


def merge_enabler(files):
    if len(files) < 2:
        (js.document.getElementById('action-button'
                                    ).setAttribute('disabled', True))
    else:
        (js.document.getElementById('action-button'
                                    ).removeAttribute('disabled'))
    
def create_dropdiv():
    el = js.document.createElement('div')
    el.classList.add('pdf-div')
    line = js.document.createElement('hr')
    line.setAttribute('color', 'crimson')
    line.setAttribute('size', 3)
    line.setAttribute('width', '100%')
    el.appendChild(line)
    js.document.getElementById('target').appendChild(el)
    add_event_listener(el, 'dragenter', enter_div)
    add_event_listener(el, 'dragover', enter_div)
    add_event_listener(el, 'dragleave', leave_div)
    add_event_listener(el, 'drop', pdf_merge.drop_div)
  
  
def create_div(f):
    el = js.document.createElement('div')
    el.innerHTML = f.name
    el.innerHTML += f'<p style="font-size:4vh;color:gray;">{str(merge_pdf.order)}</p>'
    el.classList.add('pdf')
    el.setAttribute('draggable', True)
    js.document.getElementById('target').appendChild(el)
    add_event_listener(el, 'mouseenter', show_tooltip)
    add_event_listener(el, 'mouseleave', hide_tooltip)
    add_event_listener(el, 'dragstart', pdf_merge.drag_start)
    add_event_listener(el, 'dragend', drag_end)


class PdfMerge:

    def __init__(self):
        self.files = []
        self.merger = PdfWriter()
        self.order = 1
    
    def write_pdf(self, evt):
        self.merger.append(io.BytesIO(bytes(evt.target.result.to_py())))
        
    def select_files(self, evt):
        if evt.target.id == 'selector':
            modify_canvas()
            Div(self.order)
        filelist = evt.target.files
        for f in filelist:
            create_div(f)
            self.files.append(f)
            create_dropdiv()
            if len(self.files) % 3 == 0:
                create_dropdiv()
            self.order += 1
        evt.target.value = ''
        merge_enabler(self.files)
    
    def drop_files(self, evt):
        js.document.getElementById('div-drag').style.display = 'none'
        evt.preventDefault()
        if len(self.files) == 0:
            modify_canvas()
            Div(self.order)
        for i in evt.dataTransfer.items:
            if i.kind == 'file':
                f = i.getAsFile()
                create_div(f)
                self.files.append(f)
                create_dropdiv()
                if len(self.files) % 3 == 0:
                    create_dropdiv()
                self.order += 1
        merge_enabler(self.files)
    
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
    
    def drag_start(self, evt):
        tt = js.document.getElementById('tooltip')
        if tt in js.document.body.children:
            js.document.body.removeChild(tt)
        evt.target.classList.add('draggable')
        evt.dataTransfer.effectAllowed = 'move'
        self.index = int(order(evt.target.getBoundingClientRect().x,
                               evt.target.getBoundingClientRect().y, 14))
        
    def drop_div(self, evt):
        evt.preventDefault()
        for c in evt.target.children:
            c.style.visibility = 'hidden'
        index = int(order(evt.target.getBoundingClientRect().x,
                          evt.target.getBoundingClientRect().y, 12))
        if self.index > index:
            self.files.insert(index, self.files.pop(self.index))
        elif self.index == index:
            pass
        else:
            self.files.insert(index, self.files[self.index])
            del self.files[self.index]
        for d, f in zip(js.document.querySelectorAll("div.pdf"), self.files):
            d.innerHTML.replace(d.innerHTML.split('<p style:"')[0], f.name)

    

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