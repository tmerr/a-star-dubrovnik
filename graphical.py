import lab1
from lab1 import m_per_lat, m_per_lon

try:
    from Tkinter import *
except:
    from tkinter import *


WINWIDTH = 600
WINHEIGHT = 600


def norm(x_m, y_m):
    lat = y_m / m_per_lat
    lon = x_m / m_per_lon
    norm_lat = 1 - max(0, min(1, lat - 42))
    norm_lon = max(0, min(1, lon - 18))

    return (norm_lon, norm_lat)


def create_lines(id_digraph, id_to_data):
    visited = set()
    lines = []
    for source in id_digraph:
        visited.add(source)
        for dest in id_digraph[source]:
            if not dest in visited:
                s = id_to_data[source]
                d = id_to_data[dest]

                line = { norm(s.x_m, s.y_m), norm(d.x_m, d.y_m) }
                if len(line) == 2:
                    lines.append(line)

    return lines


class MyWin(Frame):
    '''
    Here is a Tkinter window with a canvas, a button, and a text label
    ''' 

    def __init__(self, master, id_digraph, id_to_data, path, cost):
        self.id_to_data = id_to_data
        self.path = path

        self.last_x = 0
        self.last_y = 0
        self.scale = 1

        thewin = Frame(master)
        self.master = master
        w = Canvas(thewin, width=WINWIDTH, height=WINHEIGHT, cursor="crosshair")

        w.create_rectangle(0, 0, WINWIDTH, WINHEIGHT, outline="#fff", fill='#fff')
        w.configure(background='white')

        w.configure(yscrollincrement='1')
        w.configure(xscrollincrement='1')

        # click drag
        w.bind("<Button-1>", self.click)
        w.bind("<B1-Motion>", self.move)

        # scroll wheel
        w.bind('<4>', self.zoom_in)
        w.bind('<5>', self.zoom_out)

        self.canvas = w
         
        self.lines = create_lines(id_digraph, id_to_data)

        pathdata = [id_to_data[nd_id] for nd_id in path]
        self.path = [norm(nd.x_m, nd.y_m) for nd in pathdata]

        self.update_lines()

        w.pack(fill=BOTH)

        thewin.pack()


    def update_lines(self):
        self.canvas.delete("all")

        wd = WINWIDTH
        h = WINHEIGHT
        s = self.scale
        for (lon1, lat1), (lon2, lat2) in self.lines:
            self.canvas.create_line(s*wd*lon1, s*h*lat1, s*wd*lon2, s*h*lat2, fill='grey')

        '''
        for i in range(0, 3601):
            self.canvas.create_line(s*wd*float(i)/3600, 0, s*wd*float(i)/3600, 1*s*h)

        for i in range(0, 3601):
            self.canvas.create_line(0, s*h*float(i)/3600, 1*s*wd, s*wd*float(i)/3600)
        '''

        paths2 = [(s*wd*lon, s*h*lat) for (lon, lat) in self.path]
        self.canvas.create_line(*paths2, fill='red')


    def shift(self, dx, dy):
        self.canvas.xview('scroll', int(dx), 'units')
        self.canvas.yview('scroll', int(dy), 'units')
        

    def zoom_in(self, event):
        self.scale *= 1.1
        self.update_lines()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.shift(x*.1, y*.1)


    def zoom_out(self, event):
        self.scale /= 1.1
        self.update_lines()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.shift(-x*(1-1/1.1), -y*(1-1/1.1))


    def click(self, event):
        self.last_x = event.x
        self.last_y = event.y


    def move(self, event):
        self.shift(self.last_x - event.x, self.last_y - event.y)
        self.last_x = event.x
        self.last_y = event.y


def display(graph, data, path, cost):
    """Display the map (as a graph of node ids) and the given path through it (a list of node ids)"""
    master = Tk()
    thewin = MyWin(master, graph, data, path, cost)
    mainloop()
