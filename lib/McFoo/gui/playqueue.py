from Tkinter import *
import McFoo.gui.list

import Pmw

class PlayQueue:
    def __init__(self, master, xrpc):
        self.master = master
        pane = Pmw.PanedWidget(master)

        pane.add("History")
        self.history=McFoo.gui.list.DraggableList(pane.pane("History"))
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)

        pane.add("Current song")
        self.playing=McFoo.gui.list.DraggableLabel(pane.pane("Current song"))

        pane.add("Playqueue")
        self.queue=McFoo.gui.list.ReorderableList(pane.pane("Playqueue"))
#        self.queue.listbox.selectmode=EXTENDED
##        self.history.listbox.bind("<Double-Button-1>", self.say_hi)
	self.queue.notify_move=self.notify_move
	self.queue.notify_copy=self.notify_copy
	self.queue.notify_drag_start=self.notify_drag_start
	self.queue.notify_drag_end=self.notify_drag_end

	pane.pack(expand=1, fill='both')

        buttonbar = Frame(master)
        self.pause_button = Button(buttonbar, text="Pause", command=self.pause)
        self.pause_button.pack(side=LEFT)
        self.next_button = Button(buttonbar, text="Next", command=self.next)
        self.next_button.pack(side=LEFT)
        self.trash_button = Button(buttonbar, text="Trash", command=self.trash)
        self.trash_button.pack(side=RIGHT)
        buttonbar.pack(fill=X)

        self.xrpc=xrpc
        self._dragging=0
        self.serial=0
        self._timer=None
        self._timed_refresh()

    def pause(self):
        self._rpc('mcfoo.pauseorplay', [])

    def next(self):
        self._rpc('mcfoo.next', [])
        # TODO the refresh happens too soon, the effect of next
        # won't probably be visible yet..
        self.refresh()

    def trash(self):
        self._rpc('mcfoo.delete', map(lambda x: x['id'],self.queue.selected()))
        self.refresh()

    def _timed_refresh(self):
        if not self._dragging:
            self.refresh()
        self._timed_refresh_setup()

    def _timed_refresh_setup(self):
        if self._timer:
            self.master.after_cancel(self._timer)
        self._timer=self.master.after(10000, self._timed_refresh)

    def refresh(self):
        s=self._rpc('mcfoo.list', [self.serial])
        if s.has_key('history'):
            self.history[:]=s['history'][:-1]
            self.playing.set(s['history'][-1])
        if s.has_key('queue'):
            self.queue[:]=s['queue']
        self.serial=s['serial']
        self._timed_refresh_setup()

    def notify_move(self, changes):
        # changes = [(newloc, song), (newloc, song), ..]
        self._rpc('mcfoo.moveabs',
                  map(lambda (newloc, song):
                      (song['id'], newloc),changes))
        self.refresh()

    def notify_copy(self, changes):
        # changes = [(newloc, song), (newloc, song), ..]
        self._rpc('mcfoo.addqueueidx',
                  map(lambda (newloc, song):
                      (song['priority'], song['backend'], song['media'], song['name'], newloc),changes))
        self.refresh()

    def notify_drag_start(self):
        self._dragging=1

    def notify_drag_end(self):
        self._dragging=0

    def _rpc(self, command, params):
        return self.xrpc.execute(command, params)
