import lab1
from lab1 import m_per_lat, m_per_lon

try:
    from Tkinter import *
except:
    from tkinter import *


WINWIDTH = 500
WINHEIGHT = 500


def create_lines(id_digraph, id_to_data):
    left = float('inf')
    right = float('-inf')
    top = float('-inf')
    bottom = float('inf')

    visited = set()
    lines = []
    for source in id_digraph:
        visited.add(source)
        for dest in id_digraph[source]:
            if not dest in visited:
                s = id_to_data[source]
                d = id_to_data[dest]

                left = min(left, s.x_m, d.x_m)
                right = max(right, s.x_m, d.x_m)
                bottom = min(bottom, s.y_m, d.y_m)
                top = max(top, s.y_m, d.y_m)

                line = { (s.x_m, s.y_m), (d.x_m, d.y_m) }
                lines.append(line)

    width = right - left
    height = top - bottom

    def norm(x, y):
        return ((x - left)/width, 1-(y-bottom)/height)

    def fit(x, y):
        return (x*WINWIDTH, y*WINHEIGHT)

    fit_lines = [{fit(*norm(*p1)), fit(*norm(*p2))} for p1, p2 in lines]

    return fit_lines


class MyWin(Frame):
    '''
    Here is a Tkinter window with a canvas, a button, and a text label
    '''
    def __init__(self, master, id_digraph, id_to_data, optimal_path, cost):
        thewin = Frame(master)
        w = Canvas(thewin, width=WINWIDTH, height=WINHEIGHT, cursor="crosshair")

        w.bind("<Button-1>", self.mapclick)
        #w.bind("<Motion>", self.maphover)

        lines = create_lines(id_digraph, id_to_data)
        for ((x1, y1), (x2, y2)) in lines:
            w.create_line(x1, y1, x2, y2)

        w.pack(fill=BOTH) # put canvas in window, fill the window

        self.canvas = w # save the canvas object to talk to it later

        cb = Button(thewin, text="Button", command=self.click)
        # put the button in the window, on the right
        # I really have not much idea how Python/Tkinter layout managers work
        cb.pack(side=RIGHT,pady=5)

        thewin.pack()

    def click(self):
        print("Clicky!")

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
