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

import math

import gobject
import gtk
import cairo
import pango
import pangocairo

MOVE_TIMEOUT = 20
DISTANCE_MIN = 40
DISTANCE_MAX = 80

class Plot(gobject.GObject):

    moving = False
    zoom_level_x = 1.0
    zoom_level_y = 1.0

    offset_x = 300
    offset_y = 225

    def __init__(self):

        self.window = gtk.Window()
        self.window.set_title("Cairo Plot")
        self.window.set_size_request(600, 450)

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
            self.zoom_level_x *= 1.1
            self.zoom_level_y *= 1.1
        else:
            self.zoom_level_x *= .9
            self.zoom_level_y *= .9
        self.draw()


    def button_press_cb(self, source, event):

        self.moving = True
        self.move(*self.display.get_pointer()[1:-1])


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

        gobject.timeout_add(MOVE_TIMEOUT, self.move, new_x, new_y)


    def expose_cb(self, source, event):

        self.draw()


    def draw(self):

        ctx = self.drawing_area.window.cairo_create()
        ctx.translate(self.offset_x + .5, self.offset_y + .5)

        ctx.save()
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.paint()
        ctx.restore()

        width, height = self.drawing_area.get_allocation().width, self.drawing_area.get_allocation().height

        self.draw_axes(ctx, width, height)
        self.draw_func(ctx, width, height)


    def draw_axes(self, ctx, width, height):

        bound_left = - self.offset_x
        bound_right = width - self.offset_x
        bound_top = - self.offset_y
        bound_bottom = height - self.offset_y

        # Draw axes..
        ctx.move_to(bound_left, 0)
        ctx.line_to(bound_right, 0)
        ctx.move_to(0, bound_top)
        ctx.line_to(0, bound_bottom)

        ctx.set_line_width(1.0)
        ctx.stroke()

        # Draw markers...
        step = 1.0
        dist = self.zoom_level_x * 40
        while dist > DISTANCE_MAX:
            dist /= 2
            step /= 2

        while dist < DISTANCE_MIN:
            dist *= 2
            step *= 2

        position = (bound_left // dist) * dist
        while position <= (bound_right // dist) * dist:
            ctx.move_to(position, -5)
            ctx.line_to(position, 5)
            ctx.stroke()

            mark = str(round(position / dist * step, 2))
            ctx.move_to(position, 10)

            pango_ctx = pangocairo.CairoContext(ctx)
            layout = pango_ctx.create_layout()
            layout.set_text(mark)
            pango_ctx.show_layout(layout)

            position += dist

        zf = 2 ** round(math.log(self.zoom_level_x, 2), 0)
        nkst = math.log(zf/2, 2)
        print nkst, self.zoom_level_x


    def draw_func(self, ctx, width, height):

        ctx.move_to(0, 0)

        ctx.scale(self.zoom_level_x, self.zoom_level_y)
        ctx.line_to(40, 40)
        ctx.scale(1 / self.zoom_level_x, 1 / self.zoom_level_y)
        ctx.stroke()


class CairoPlot(object):

    def __init__(self):

        self.plot = Plot()


if __name__ == '__main__':
    cairo_plot = CairoPlot()
    gtk.main()
