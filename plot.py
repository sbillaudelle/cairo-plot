#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import gobject
import gtk
import cairo

class Plot(gobject.GObject):

    moving = False
    zoom_level = 1.0

    offset_x = 0
    offset_y = 0

    def __init__(self):

        self.window = gtk.Window()

        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.set_events(gtk.gdk.ALL_EVENTS_MASK)
        self.drawing_area.connect('expose-event', self.expose_cb)
        self.drawing_area.connect('scroll-event', self.scroll_cb)
        self.drawing_area.connect('button-press-event', self.button_press_cb)
        self.drawing_area.connect('button-release-event', self.button_release_cb)

        self.window.add(self.drawing_area)
        self.window.show_all()

        self.display = self.window.get_display()


    def scroll_cb(self, source, event):

        if event.direction == gtk.gdk.SCROLL_UP:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= .9
        self.draw()


    def button_press_cb(self, source, event):

        self.moving = True
        gobject.timeout_add(50, self.move, *self.display.get_pointer()[1:-1])


    def button_release_cb(self, source, event):

        self.moving = False


    def move(self, old_x=None, old_y=None):

        if not self.moving:
            return

        new_x, new_y = self.display.get_pointer()[1:-1]

        if old_x and old_y:
            self.offset_x += new_x - old_x
            self.offset_y += new_y - old_y
            self.draw()

        gobject.timeout_add(50, self.move, new_x, new_y)


    def expose_cb(self, source, event):

        self.draw()


    def draw(self):

        ctx = self.drawing_area.window.cairo_create()

        ctx.translate(self.offset_x, self.offset_y)

        ctx.scale(self.zoom_level, self.zoom_level)
        ctx.set_line_width(1.0 / self.zoom_level)

        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.paint()

        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.move_to(0, 0)
        ctx.line_to(100, 100)
        ctx.stroke()


class CairoPlot(object):

    def __init__(self):

        self.plot = Plot()


if __name__ == '__main__':
    cairo_plot = CairoPlot()
    gtk.main()
