import asyncio
import io
import js
from pyscript import Element
from pyodide.ffi import to_js
from pyodide.ffi.wrappers import add_event_listener, create_proxy
from pypdf import PdfWriter

# TO DO:
# - Gestione errore PDF
# - Supporto mobile


# Utilities


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


async def to_memview(f):
    array = await f.arrayBuffer()
    return array.to_py()


# Layout


def show_menu():
    navbar = js.document.getElementById('top-menu')
    if navbar.className == 'menu':
        navbar.className += ' responsive'
    else:
        navbar.className = 'menu'


def merge_enabler(files):
    if len(files) < 2:
        (js.document.getElementById('action-button'
                                    ).setAttribute('disabled', True))
    else:
        (js.document.getElementById('action-button'
                                    ).removeAttribute('disabled'))


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
    el.innerHTML = f'<span>{f.name}</span>'
    el.innerHTML += f'<p style="font-size:4vh;color:gray;">\
        {str(pdf_merge.order)}</p>'
    el.classList.add('pdf')
    el.setAttribute('draggable', True)
    js.document.getElementById('target').appendChild(el)
    add_event_listener(el, 'mouseenter', show_tooltip)
    add_event_listener(el, 'mouseleave', hide_tooltip)
    add_event_listener(el, 'dragstart', pdf_merge.drag_start)
    add_event_listener(el, 'dragend', drag_end)


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
    add_event_listener(js.document.getElementById('bin'),
                       'dragenter', do_nothing)
    add_event_listener(js.document.getElementById('bin'),
                       'dragover', do_nothing)
    add_event_listener(js.document.getElementById('bin'),
                       'dragleave', do_nothing)
    add_event_listener(js.document.getElementById('bin'),
                       'drop', pdf_merge.delete_file)


# Callbacks


def write_file(content, callback):
    blob = js.Blob.new([content], {type: "application/pdf"})
    callback(blob)


# Events


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
    js.document.getElementById('bin').style.display = 'none'


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
    tt.innerHTML = evt.target.firstChild.innerHTML
    js.document.body.appendChild(tt)


def hide_tooltip(evt):
    tt = js.document.getElementById('tooltip')
    if tt in js.document.body.children:
        js.document.body.removeChild(tt)


def enter_div(evt):
    evt.preventDefault()
    for c in evt.target.children:
        c.style.visibility = 'visible'


def do_nothing(evt):
    evt.preventDefault()


def leave_div(evt):
    evt.preventDefault()
    for c in evt.target.children:
        c.style.visibility = 'hidden'


# Class PdfMerge

class PdfMerge:

    def __init__(self):
        self.files = []
        self.merger = PdfWriter()
        self.order = 1
    
    def select_files(self, evt):
        if evt.target.id == 'selector':
            modify_canvas()
        for f in evt.target.files:
            if len(self.files) % 3 == 0:
                create_dropdiv()
            create_div(f)
            self.files.append(f)
            create_dropdiv()
            self.order += 1
        evt.target.value = ''
        merge_enabler(self.files)
    
    def drop_files(self, evt):
        js.document.getElementById('div-drag').style.display = 'none'
        evt.preventDefault()
        if len(self.files) == 0:
            modify_canvas()
        for i in evt.dataTransfer.items:
            if i.kind == 'file':
                if len(self.files) % 3 == 0:
                    create_dropdiv()
                f = i.getAsFile()
                create_div(f)
                self.files.append(f)
                create_dropdiv()
                self.order += 1
        merge_enabler(self.files)
    
    async def read_files(self, f):
        mv = await to_memview(f)
        if '%PDF' in str(bytes(mv)[:4]):
            self.merger.append(io.BytesIO(bytes(mv)))
        else:
            pass # Gestire errore
    
    async def merge_files(self, evt):
        js.document.body.style.cursor = 'wait'
        evt.target.style.cursor = 'wait'
        for f in self.files:
            await self.read_files(f)
        self.write_merged(write_file)
    
    def write_merged(self, callback):
        with io.BytesIO() as output:
            self.merger.write(output)
            self.merger.close()
            output.seek(0)
            content = to_js(output.read())
        callback(content, self.download_file)
    
    def download_file(self, blob):
        js.document.body.style.cursor = 'default'
        url = js.window.URL.createObjectURL(blob)
        link = js.document.createElement('a')
        link.setAttribute('href', url)
        link.setAttribute('download', 'merged_pdf.pdf')
        link.style.display = 'none'
        js.document.body.appendChild(link)
        link.click()
        js.document.body.removeChild(link)
        js.window.location.reload()
    
    def drag_start(self, evt):
        tt = js.document.getElementById('tooltip')
        if tt in js.document.body.children:
            js.document.body.removeChild(tt)
        js.document.getElementById('bin').style.display = 'flex'
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
            d.firstChild.innerHTML = f.name


    def delete_file(self, evt):
        evt.preventDefault()
        del self.files[self.index]
        js.document.getElementById('target').innerHTML = ''
        self.order = 1
        for n, f in enumerate(self.files):
            if n % 3 == 0:
                create_dropdiv()
            create_div(f)
            create_dropdiv()
            self.order += 1
        merge_enabler
            


# Main routine


pdf_merge = PdfMerge()
setup()
    