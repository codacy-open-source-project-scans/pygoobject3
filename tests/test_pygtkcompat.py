# -*- Mode: Python; py-indent-offset: 4 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

import unittest
import base64
import warnings

import pytest
import gi
import pygtkcompat
from pygtkcompat.pygtkcompat import _disable_all as disable_all

from .helper import capture_gi_deprecation_warnings, capture_glib_warnings

try:
    from gi.repository import Gtk, Gdk
except ImportError:
    Gtk = None
else:
    if Gtk._version != "3.0":
        Gtk = None


class TestGlibCompat(unittest.TestCase):

    def setUp(self):
        with warnings.catch_warnings(record=True):
            pygtkcompat.enable()

    def tearDown(self):
        disable_all()

    def test_import(self):
        import glib
        import gio
        glib, gio


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestMultipleEnable(unittest.TestCase):

    def tearDown(self):
        disable_all()

    def test_main(self):
        with warnings.catch_warnings(record=True):
            pygtkcompat.enable()
            pygtkcompat.enable()

    def test_gtk(self):
        pygtkcompat.enable_gtk("3.0")
        pygtkcompat.enable_gtk("3.0")
        import gtk

        # https://bugzilla.gnome.org/show_bug.cgi?id=759009
        w = gtk.Window()
        w.realize()
        self.assertEqual(len(w.window.get_origin()), 2)
        w.destroy()

    def test_gtk_no_4(self):
        self.assertRaises(ValueError, pygtkcompat.enable_gtk, version='4.0')

    def test_gtk_version_conflict(self):
        pygtkcompat.enable_gtk("3.0")
        self.assertRaises(ValueError, pygtkcompat.enable_gtk, version='2.0')


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestATKCompat(unittest.TestCase):

    def setUp(self):
        pygtkcompat.enable_gtk("3.0")

    def tearDown(self):
        disable_all()

    def test_object(self):
        import atk
        self.assertTrue(hasattr(atk, 'Object'))


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestPangoCompat(unittest.TestCase):

    def setUp(self):
        pygtkcompat.enable_gtk("3.0")

    def tearDown(self):
        disable_all()

    def test_layout(self):
        import pango
        self.assertTrue(hasattr(pango, 'Layout'))


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestPangoCairoCompat(unittest.TestCase):

    def setUp(self):
        pygtkcompat.enable_gtk("3.0")

    def tearDown(self):
        disable_all()

    def test_error_underline_path(self):
        import pangocairo
        self.assertTrue(hasattr(pangocairo, 'error_underline_path'))


@unittest.skipUnless(Gtk, 'Gtk not available')
class TestGTKCompat(unittest.TestCase):

    def setUp(self):
        pygtkcompat.enable_gtk("3.0")

    def tearDown(self):
        disable_all()

    def test_window_get_frame_extents(self):
        import gtk
        import gtk.gdk
        w = gtk.Window()
        w.realize()
        rect = w.window.get_frame_extents()
        assert isinstance(rect, gtk.gdk.Rectangle)

    def test_window_get_geometry(self):
        import gtk
        w = gtk.Window()
        w.realize()
        with capture_gi_deprecation_warnings():
            geo = w.window.get_geometry()
        assert isinstance(geo, tuple)
        assert len(geo) == 5

    def test_action_set_tool_item_type(self):
        import gtk
        with pytest.warns(gi.PyGIDeprecationWarning):
            gtk.Action().set_tool_item_type(gtk.Action)

    def test_treeviewcolumn_pack(self):
        import gtk
        col = gtk.TreeViewColumn()
        col.pack_end(gtk.CellRendererText())
        col.pack_start(gtk.CellRendererText())

    def test_cell_layout_pack(self):
        import gtk
        layout = gtk.EntryCompletion()
        layout.pack_end(gtk.CellRendererText())
        layout.pack_start(gtk.CellRendererText())

    def test_cell_layout_cell_data_func(self):
        import gtk

        def func(*args):
            pass

        layout = gtk.EntryCompletion()
        render = gtk.CellRendererText()
        layout.set_cell_data_func(render, func)

    def test_combo_row_separator_func(self):
        import gtk

        def func(*args):
            pass

        combo = gtk.ComboBox()
        combo.set_row_separator_func(func)

    def test_container_install_child_property(self):
        import gtk

        box = gtk.Box()
        with pytest.warns(gi.PyGIDeprecationWarning):
            box.install_child_property(0, None)

    def test_combo_box_new_text(self):
        import gtk

        combo = gtk.combo_box_new_text()
        assert isinstance(combo, gtk.ComboBox)
        combo.append_text("foo")

    def test_scale(self):
        import gtk

        adjustment = gtk.Adjustment()
        assert gtk.HScale()
        assert gtk.HScale(adjustment).get_adjustment() == adjustment
        adjustment = gtk.Adjustment()
        assert gtk.VScale()
        assert gtk.VScale(adjustment).get_adjustment() == adjustment

    def test_stock_add(self):
        import gtk

        gtk.stock_add([])

    def test_text_view_scroll_to_mark(self):
        import gtk

        view = gtk.TextView()
        buf = view.get_buffer()
        mark = gtk.TextMark(name="foo")
        buf.add_mark(mark, buf.get_end_iter())
        view.scroll_to_mark(mark, 0.0)

    def test_window_set_geometry_hints(self):
        import gtk

        w = gtk.Window()
        w.set_geometry_hints(None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        w.set_geometry_hints(None, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1)
        with pytest.raises(TypeError):
            w.set_geometry_hints(None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def test_buttons(self):
        import gtk.gdk
        self.assertEqual(gtk.gdk._2BUTTON_PRESS, 5)
        self.assertEqual(gtk.gdk.BUTTON_PRESS, 4)

    def test_enums(self):
        import gtk
        self.assertEqual(gtk.WINDOW_TOPLEVEL, Gtk.WindowType.TOPLEVEL)
        self.assertEqual(gtk.PACK_START, Gtk.PackType.START)

    def test_flags(self):
        import gtk
        self.assertEqual(gtk.EXPAND, Gtk.AttachOptions.EXPAND)
        self.assertEqual(gtk.gdk.SHIFT_MASK, Gdk.ModifierType.SHIFT_MASK)

    def test_keysyms(self):
        import gtk.keysyms
        self.assertEqual(gtk.keysyms.Escape, Gdk.KEY_Escape)
        self.assertTrue(gtk.keysyms._0, Gdk.KEY_0)

    def test_style(self):
        import gtk
        widget = gtk.Button()
        with capture_gi_deprecation_warnings():
            widget.get_style_context().set_state(gtk.STATE_NORMAL)
            self.assertTrue(isinstance(widget.style.base[gtk.STATE_NORMAL],
                                       gtk.gdk.Color))

    def test_alignment(self):
        import gtk
        # Creation of pygtk.Alignment causes hard warnings, ignore this in testing.
        with capture_glib_warnings(allow_warnings=True):
            a = gtk.Alignment()

        self.assertEqual(a.props.xalign, 0.0)
        self.assertEqual(a.props.yalign, 0.0)
        self.assertEqual(a.props.xscale, 0.0)
        self.assertEqual(a.props.yscale, 0.0)

    def test_box(self):
        import gtk
        box = gtk.Box()
        child = gtk.Button()

        box.pack_start(child)
        expand, fill, padding, pack_type = box.query_child_packing(child)
        self.assertTrue(expand)
        self.assertTrue(fill)
        self.assertEqual(padding, 0)
        self.assertEqual(pack_type, gtk.PACK_START)

        child = gtk.Button()
        box.pack_end(child)
        expand, fill, padding, pack_type = box.query_child_packing(child)
        self.assertTrue(expand)
        self.assertTrue(fill)
        self.assertEqual(padding, 0)
        self.assertEqual(pack_type, gtk.PACK_END)

    def test_combobox_entry(self):
        import gtk
        liststore = gtk.ListStore(int, str)
        liststore.append((1, 'One'))
        liststore.append((2, 'Two'))
        liststore.append((3, 'Three'))
        # might cause a Pango warning, do not break on this
        with capture_glib_warnings(allow_warnings=True):
            combo = gtk.ComboBoxEntry(model=liststore)
        combo.set_text_column(1)
        combo.set_active(0)
        self.assertEqual(combo.get_text_column(), 1)
        self.assertEqual(combo.get_child().get_text(), 'One')
        combo = gtk.combo_box_entry_new()
        combo.set_model(liststore)
        combo.set_text_column(1)
        combo.set_active(0)
        self.assertEqual(combo.get_text_column(), 1)
        self.assertEqual(combo.get_child().get_text(), 'One')
        combo = gtk.combo_box_entry_new_with_model(liststore)
        combo.set_text_column(1)
        combo.set_active(0)
        self.assertEqual(combo.get_text_column(), 1)
        self.assertEqual(combo.get_child().get_text(), 'One')

    def test_size_request(self):
        import gtk
        box = gtk.Box()
        with capture_gi_deprecation_warnings():
            self.assertEqual(box.size_request(), [0, 0])

    def test_pixbuf(self):
        import gtk.gdk
        gtk.gdk.Pixbuf()

    def test_pixbuf_loader(self):
        import gtk.gdk
        # load a 1x1 pixel PNG from memory
        data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP4n8Dw'
                                'HwAGIAJf85Z3XgAAAABJRU5ErkJggg==')
        loader = gtk.gdk.PixbufLoader('png')
        loader.write(data)
        loader.close()

        pixbuf = loader.get_pixbuf()
        self.assertEqual(pixbuf.get_width(), 1)
        self.assertEqual(pixbuf.get_height(), 1)

    def test_pixbuf_formats(self):
        import gtk.gdk
        formats = gtk.gdk.pixbuf_get_formats()
        self.assertEqual(type(formats[0]), dict)
        self.assertTrue('name' in formats[0])
        self.assertTrue('description' in formats[0])
        self.assertTrue('mime_types' in formats[0])
        self.assertEqual(type(formats[0]['extensions']), list)

    def test_gdk_window(self):
        import gtk
        w = gtk.Window()
        w.realize()
        origin = w.get_window().get_origin()
        self.assertTrue(isinstance(origin, tuple))
        self.assertEqual(len(origin), 2)
