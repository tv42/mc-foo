from Tkinter import *
import McFoo.gui.list
import McFoo.gui.song
import McFoo.volume
import McFoo.playqueue
import McFoo.dj

import Pmw

class VolumeObserverFan(McFoo.volume.VolumeObserver):
    def __init__(self, callback):
        McFoo.volume.VolumeObserver.__init__(self)
        self.callback=callback

    def remote_change(self, left, right):
        self.callback((left+right)/2.0)

class DjObserverFan(McFoo.dj.DjObserver):
    def __init__(self, callback):
        McFoo.dj.DjObserver.__init__(self)
        self.callback=callback

    def remote_change(self, at):
        self.callback(at)

class HistoryObserverFan(McFoo.playqueue.HistoryObserver):
    maxlen=10
    
    def __init__(self, history, playing):
        McFoo.playqueue.HistoryObserver.__init__(self)
        self.history=history
        self.playing=playing

    def remote_snapshot(self, history):
        self.history[:]=map(lambda s: McFoo.gui.song.GuiSong(s), history[:-1])
        try:
            h=history[-1]
        except IndexError:
            pass
        else:
            self.playing.set(McFoo.gui.song.GuiSong(h))

    def remote_add(self, song):
        self.history.append(self.playing.get())
        while len(self.history)>self.maxlen:
            del self.history[0]
        self.playing.set(McFoo.gui.song.GuiSong(song))

class PlayqueueObserverFan(McFoo.playqueue.PlayqueueObserver):
    def __init__(self, queue):
        McFoo.playqueue.PlayqueueObserver.__init__(self)
        self.queue=queue

    def remote_snapshot(self, queue):
        self.queue[:]=map(lambda s: McFoo.gui.song.GuiSong(s), queue)

    def remote_insert(self, idx, song):
        self.queue[idx:idx]=[McFoo.gui.song.GuiSong(song)]

    def remote_remove(self, idx):
        self.queue[idx:idx+1]=[]

    def remote_move(self, oldidx, newidx):
        tmp=self.queue[oldidx]
        self.queue[oldidx:oldidx+1]=[]
        self.queue.insert(newidx, tmp)

class PlayQueue:
    def __init__(self, master, remote):
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
        self.volume = Scale(buttonbar, orient=HORIZONTAL, bigincrement=1, \
                            showvalue=0, command=self.set_volume)
        self.volume.pack(side=LEFT)
        self.location = Scale(buttonbar, orient=HORIZONTAL,
                              showvalue=0, resolution=0.01, to=1.0,
                              command=self.set_location) #TODO bigincrement?
        self.location.pack(side=LEFT, fill=X, expand=1)
        self.trash_button = Button(buttonbar, text="Trash", command=self.trash)
        self.trash_button.pack(side=RIGHT)
        buttonbar.pack(fill=X)

        self.remote=remote
        self._dragging=0
        self._timer=None

        self._last_volume=None
        self.remote.observe_volume(VolumeObserverFan(self.volume.set))
        self._last_location=None
        self.remote.observe_location(DjObserverFan(self.see_location))
        self.remote.observe_playqueue(PlayqueueObserverFan(self.queue))
        self.remote.observe_history(HistoryObserverFan(self.history, self.playing))

    def set_volume(self, vol):
        vol=int(vol)
        if self._last_volume!=None and self._last_volume!=vol:
            self.remote.volume_set(vol)
        self._last_volume=vol

    def see_location(self, at):
        self._last_location="%0.2f"%at
        self.location.set(at)

    def set_location(self, at):
        if self._last_location!=None and self._last_location!=at:
            self.remote.jump(float(at))
        self._last_location=at

    def pause(self):
        self.remote.pauseorplay()

    def next(self):
        self.remote.next()

    def trash(self):
        self.remote.delete(map(lambda x: x['id'],self.queue.selected()))

    def notify_move(self, changes):
        # changes = [(newloc, song), (newloc, song), ..]
        self.remote.moveabs(map(lambda (newloc, song):
                                (song['id'], newloc),changes))

    def notify_copy(self, changes):
        # changes = [(newloc, song), (newloc, song), ..]
        self.remote.addqueueidx(map(lambda (newloc, song):
                                    (song['priority'],
                                     song['backend'],
                                     song['media'],
                                     song['name'], newloc),
                                    changes))

    def notify_drag_start(self):
        self._dragging=1

    def notify_drag_end(self):
        self._dragging=0
