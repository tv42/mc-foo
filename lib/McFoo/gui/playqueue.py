from Tkinter import *
import McFoo.gui.list

import Pmw

class PlayQueue:
    def __init__(self, master, xrpc):
        self.master = master
        pane = Pmw.PanedWidget(master)

        pane.add("History")
        self.history=McFoo.gui.list.ReorderableList(pane.pane("History"))
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)

        pane.add("Playqueue")
        self.queue=McFoo.gui.list.ReorderableList(pane.pane("Playqueue"))
#        self.queue.listbox.selectmode=EXTENDED
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)
	self.queue.notify_move=self.notify_move
	self.queue.notify_drag_start=self.notify_drag_start
	self.queue.notify_drag_end=self.notify_drag_end

	pane.pack(expand=1, fill='both')

        self.xrpc=xrpc
        self._dragging=0
        self.serial=0
        self._timed_refresh()

    def _timed_refresh(self):
        if not self._dragging:
            self.refresh()
        self.master.after(10000, self._timed_refresh)

    def refresh(self):
        s=self._rpc('mcfoo.list', [self.serial])
        if s.has_key('history'):
            self.history[:]=s['history']
        if s.has_key('queue'):
            self.queue[:]=s['queue']
        self.serial=s['serial']

    def notify_move(self, changes):
        # changes = [(newloc, song), (newloc, song), ..]
        self._rpc('mcfoo.moveabs',
                  map(lambda (newloc, song):
                      (song['id'], newloc),changes))

    def notify_drag_start(self):
        self._dragging=1

    def notify_drag_end(self):
        self._dragging=0

    def _rpc(self, command, params):
        return self.xrpc.execute(command, params)
