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

    def __init__(self, master, id_digraph, id_to_data, optimal_path, cost):
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

        w.bind("<Button-1>", self.click)
        w.bind("<B1-Motion>", self.move)

        # scroll wheel
        w.bind('<4>', self.zoom_in)
        w.bind('<5>', self.zoom_out)

        self.canvas = w
         
        self.lines = create_lines(id_digraph, id_to_data)
        self.update_lines()

        w.pack(fill=BOTH) # put canvas in window, fill the window

        cb = Button(thewin, text="Button", command=self.click)
        # put the button in the window, on the right
        # I really have not much idea how Python/Tkinter layout managers work
        cb.pack(side=RIGHT,pady=5)

        thewin.pack()

    def update_lines(self):
        self.canvas.delete("all")
        for (lon1, lat1), (lon2, lat2) in self.lines:
            wd = WINWIDTH
            h = WINHEIGHT
            s = self.scale
            self.canvas.create_line(s*wd*lon1, s*h*lat1, s*wd*lon2, s*h*lat2)
        #self.master.update()

    def zoom_in(self, event):
        self.scale *= 1.1
        self.update_lines()

    def zoom_out(self, event):
        self.scale /= 1.1
        self.update_lines()

    def click(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def move(self, event):
        self.canvas.xview('scroll', self.last_x - event.x, 'units')
        self.canvas.yview('scroll', self.last_y - event.y, 'units')

        self.last_x = event.x
        self.last_y = event.y

    def mapclick(self,event):
        # gives the x,y location of the click
        # let's use that to move the circle
        self.canvas.coords('greendot',event.x-5,event.y-5,event.x+5,event.y+5)


if __name__ == '__main__':
    id_digraph, id_to_data = lab1.extract_info('dbv.osm', 'N42E018.HGT')
    optimal_path, cost = None, None
    #optimal_path, cost = lab1.a_star(id_digraph, id_to_data, 'A', 'E')

    master = Tk()
    thewin = MyWin(master, id_digraph, id_to_data, optimal_path, cost)

    # in Python you have to start the event loop yourself:
    mainloop()
