'''
GTK interface to `fuel`

Handles menus, user input and formats output.
'''
from gi.repository import Gtk
import string
import functions as FN

class MainMenu(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        addFuel = Gtk.Button(label="Add Fuel")
        editFuel = Gtk.Button(label="Edit Fuel")
        addService = Gtk.Button(label="Add Service")
        editService = Gtk.Button(label="Edit Service")
        summary = Gtk.Button(label="Summary")
        predict = Gtk.Button(label="Predict")
        quit = Gtk.Button(label="Quit")
        quit.connect("clicked", Gtk.main_quit)

        self.add(addFuel)
        self.attach_next_to(editFuel, addFuel, Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(addService, editFuel, Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(editService, addService, Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(summary, editService, Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(predict, summary, Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(quit, predict, Gtk.PositionType.BOTTOM, 1, 1)

class RootWindow(Gtk.Window):
    box=None
    def __init__(self):
        Gtk.Window.__init__(self, title="Fuel Economy and Service Records")

        self.box = Gtk.Grid()
        self.add(self.box)

        menu = MainMenu()
        self.box.add(menu)

#        grid = Gtk.Grid()
#        #self.box.pack_start(grid, True, True, 0)
#        self.box.add(grid)
#
        label = Gtk.Button(label="Hello World")#, halign=Gtk.Align.END)
#
        button1 = Gtk.Button(label="Click Me")
#        button1.connect("clicked", self.on_button_clicked)
#
#        button2 = Gtk.Button(label="Quit")
#        button2.connect("clicked", Gtk.main_quit)
#
#        grid.add(label)
#        grid.attach_next_to(button1, label, Gtk.PositionType.BOTTOM, 1, 1)
#        grid.attach_next_to(button2, button1, Gtk.PositionType.BOTTOM, 1, 1)
        self.box.attach(label, 1, 0, 2, 1)
        self.box.attach(button1, 1, 1, 2, 1)

    def on_button_clicked(self, widget):
        print("Boo!")
        pane = Gtk.Grid()

        name_store = Gtk.ListStore(int, str)
        name_store.append([1, "Billy Bob"])
        name_store.append([11, "Billy Bob Junior"])
        name_store.append([12, "Sue Bob"])
        name_store.append([2, "Joey Jojo"])
        name_store.append([3, "Rob McRoberts"])
        name_store.append([31, "Xavier McRoberts"])

        name_combo = Gtk.ComboBox.new_with_model(name_store)
        name_combo.connect("changed", self.on_name_combo_changed)
        name_combo.set_entry_text_column(1)
        renderer_text = Gtk.CellRendererText()
        name_combo.pack_start(renderer_text, True)
        name_combo.add_attribute(renderer_text, "text", 1)
        entry1 = Gtk.Entry()
        entry2 = Gtk.Entry()

        button = Gtk.Button(label="Click Me")
        button.connect("clicked", self.remove_pane)

        pane.add(name_combo)
        pane.attach_next_to(entry1, name_combo, Gtk.PositionType.BOTTOM, 1, 1)
        pane.attach_next_to(entry2, entry1, Gtk.PositionType.BOTTOM, 1, 1)
        pane.attach_next_to(button, entry2, Gtk.PositionType.BOTTOM, 1, 1)
        #self.box.pack_end(button, True, True, 0)

        self.box.attach(pane, 1, 0, 1, 2)
        self.show_all()

    def on_name_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            print ("Selected: ID={}, name={}".format(row_id, name))
            print(combo.get_parent().get_children())

    def remove_pane(self, widget):
        print("gone")
        self.box.remove(widget.get_parent())
        self.show_all()

class GUI:
    '''
    Wrapper
    '''
    def __init__(self):
        print('init gtk gui')

    def start(self):
        win = RootWindow()
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()
