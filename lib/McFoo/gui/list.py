from Tkinter import *
import Tkdnd
import UserList
import string

class DraggedItems(UserList.UserList):
    def __init__(self, source, data=[]):
        UserList.UserList.__init__(self, data)
        self.source=source

    def dnd_end(self, target, event):
        if target==None:
            # undo
            self.source.dnd_undo(self)

class DraggedItemsCopy(DraggedItems):
    def dnd_end(self, target, event):
        pass

class List(UserList.UserList):
    """An extended Tkinter listbox.

    All objects put here should be capable of stringifying themselves."""
    def __init__(self, master, data=[]):
        UserList.UserList.__init__(self, data)

        self.frame = Frame(master)
        self.frame.pack(fill=BOTH, expand=1)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.listbox=Listbox(self.frame)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.scrollbar.config(command=self.listbox.yview)

        self.redraw()

    def __setitem__(self, i, item):
        UserList.UserList.__setitem__(self, i, item)
        self.redraw() #TODO fix listbox intelligently
    def __delitem__(self, i):
        UserList.UserList.__delitem__(self, i)
        self.redraw() #TODO fix listbox intelligently
    def append(self, item):
        UserList.UserList.append(self, item)
        self.redraw() #TODO fix listbox intelligently
    def insert(self, i, item):
        UserList.UserList.insert(self, i, item)
        self.redraw() #TODO fix listbox intelligently
    def pop(self, i=-1):
        UserList.UserList.pop(self, i)
        self.redraw() #TODO fix listbox intelligently
    def remove(self, item):
        UserList.UserList.remove(self, item)
        self.redraw() #TODO fix listbox intelligently
    def reverse(self):
        UserList.UserList.reverse(self)
        self.redraw()
    def sort(self, cmpfunc=None):
        if cmpfunc==None:
            UserList.UserList.sort(self)
        else:
            UserList.UserList.sort(self, cmpfunc)
        self.redraw()
    def extend(self, other):
        UserList.UserList.extend(self, other)
        self.redraw() #TODO fix listbox intelligently
    def __setslice__(self, i, j, other):
        UserList.UserList.__setslice__(self, i, j, other)
        self.redraw() #TODO fix listbox intelligently
    def __delslice__(self, i, j):
        UserList.UserList.__delslice__(self, i, j)
        self.redraw() #TODO fix listbox intelligently

    def redraw(self):
        self.listbox.delete(0, END) # clear
        for entry in self.data:
            self.listbox.insert(END, str(entry))

    def selected_indexes(self):
        items = self.listbox.curselection()
        try:
            items = map(string.atoi, items)
        except ValueError:
            pass
        return items

    def idx_to_obj(self, idx):
        return map(lambda i,d=self.data: d[i], idx)

    def idx_to_idxobj(self, idx):
        return map(lambda i,d=self.data: (i, d[i]), idx)

    def selected(self):
        return self.idx_to_obj(self.selected_indexes())

    def selected_with_idx(self):
        return self.idx_to_idxobj(self.selected_indexes())

    def del_idx(self, list):
        """Delete many items."""
        list.sort()
        list.reverse()
        for i in list:
            del self[i]

    def add_tuples(self, tuples):
        """L.add_tuples(listoftuples) -- add items at indexes.

        Input looks like [(idx, item), (idx, item), ...].
        add_tuples() will add items to given indexes in sorted
        order, thus guaranteeing reasonable results."""
        order=[]
        items={}
        for idx,item in tuples:
            order.append(idx)
            items[idx]=item
        order.sort()
        for idx in order:
            self.insert(idx, items[idx])
            del items[idx]

class ReorderableList(List):
    """An extended Tkinter.Listbox with d-n-d item reordering.

    All objects put here should be capable of stringifying themselves.
    Will accept drags from any ReorderableList unless dnd_accept() is
    overridden in a subclass."""

    def __init__(self, master, data=[]):
        List.__init__(self, master, data)
        self.listbox.bind("<Button-3>", self._drag_start)
        self.listbox.dnd_accept=self.dnd_accept
        self.listbox.dnd_commit=self.dnd_commit
        self.listbox.dnd_enter=self.dnd_enter
        self.listbox.dnd_leave=self.dnd_leave
        self.listbox.dnd_motion=self.dnd_motion
        self.notify_move=None
        self.notify_copy=None
        self.notify_drag_start=None
        self.notify_drag_end=None

    def _drag_start(self, event):
        if self.notify_drag_start:
            self.notify_drag_start()
        near=self.listbox.nearest(event.y)
        if not self.listbox.select_includes(near):
            self._dnd_selection(near)
        tuples=self.selected_with_idx()
        self.del_idx(map(lambda t: t[0], tuples))
        items=DraggedItems(self, tuples)
        Tkdnd.dnd_start(items, event)
        self._dnd_selection(self.listbox.nearest(event.y))

    def dnd_accept(self, source, event):
        if isinstance(source, DraggedItems) \
           or isinstance(source, DraggedItemsCopy):
            return self.listbox
        else:
            return None

    def dnd_commit(self, source, event):
        # What index to stuff them in?
        idx=self._near(event)
        # We always add new entries _before_ the item they
        # were dragged to. This way, dragging to currently
        # playing (not in a listbox) makes the new song
        # start playing, and the last item in the playqueue
        # is always the infinite priority entry.. (TODO
        # implement that, currently there's no guarantee
        # at the server, and the gui allows dragging it)
        self[idx:idx]=map(lambda t: t[1], source)
        self.listbox.select_clear(0, END)
        self.listbox.select_set(idx, idx+len(source)-1)
        self.listbox.see(idx)
        if isinstance(source, DraggedItemsCopy):
            if self.notify_copy:
                self.notify_copy(self.selected_with_idx())
        else:
            if self.notify_move:
                self.notify_move(self.selected_with_idx())
        if self.notify_drag_end:
            self.notify_drag_end()

    def dnd_undo(self, items):
        """Undo the dnd operation, put the items back where they were."""
        print "dnd_undo"
        self.add_tuples(items)
        self.listbox.select_clear(0, END)
        for i,o in items:
            self.listbox.select_set(i)
        #TODO restore ANCHOR etc?
        if self.notify_drag_end:
            self.notify_drag_end()

    def _dnd_selection(self, idx=None):
        self.listbox.select_clear(0, END)
        if idx!=None:
            self.listbox.select_set(idx)

    def _near(self, event):
        return self.listbox.nearest(event.y_root - self.listbox.winfo_rooty())
    
    def dnd_enter(self, source, event):
        self._dnd_selection(self._near(event))
    def dnd_leave(self, source, event):
        self._dnd_selection()
    def dnd_motion(self, source, event):
        near=self._near(event)
        xoff, yoff, width, height=self.listbox.bbox(near)
        if self.listbox.bbox(near-1)==None \
           and event.y <= yoff+0.5*height:
            #scroll up
            self.listbox.yview("scroll", -1, "units")
        elif self.listbox.bbox(near+2)==None \
             and event.y >= yoff+0.5*height:
            #scroll down
            self.listbox.yview("scroll", 1, "units")

        # re-eval near to make selection reflect what the user sees
        near=self._near(event)
        self._dnd_selection(near)

class DraggableList(List):
    """An extended Tkinter.Listbox with draggable items (no drop).

    All objects put here should be capable of stringifying themselves.
    This list will only function as a source for drags -- it will
    never accept drops."""

    def __init__(self, master, data=[]):
        List.__init__(self, master, data)
        self.listbox.bind("<Button-3>", self._drag_start)

    def _drag_start(self, event):
        near=self.listbox.nearest(event.y)
        if not self.listbox.select_includes(near):
            self._dnd_selection(near)
        tuples=self.selected_with_idx()
        items=DraggedItemsCopy(self, tuples)
        Tkdnd.dnd_start(items, event)

    def _dnd_selection(self, idx=None):
        self.listbox.select_clear(0, END)
        if idx!=None:
            self.listbox.select_set(idx)

    def _near(self, event):
        return self.listbox.nearest(event.y_root - self.listbox.winfo_rooty())


class DraggableLabel(Label):
    """An extended Tkinter.Label with a draggable item (no drop).

    The object put here should be capable of stringifying itself.
    This label will only function as a source for drags -- it will
    never accept drops."""

    def __init__(self, master, content=None):
        Label.__init__(self, master)
        self.pack(fill=BOTH, expand=1)
        self.bind("<Button-3>", self._drag_start)
        self.set(content)

    def set(self, content=None):
        self.content=content
        self.config(text=content)

    def _drag_start(self, event):
        if self.content:
            items=DraggedItemsCopy(self, [(0, self.content)])
            Tkdnd.dnd_start(items, event)
