from Tkinter import *
import McFoo.gui.list

import Pmw

class PlayQueue:
    def __init__(self, master):
        pane = Pmw.PanedWidget(master)

        pane.add("History")
        self.history=McFoo.gui.list.ReorderableList(pane.pane("History"))
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)

        pane.add("Playqueue")
        self.queue=McFoo.gui.list.ReorderableList(pane.pane("Playqueue"))
#        self.queue.listbox.selectmode=EXTENDED
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)

	pane.pack(expand=1, fill='both')
