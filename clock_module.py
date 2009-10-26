# -*- coding: utf-8 -*-

import curses
import time

class ClockModule(object):
    def __init__(self, screen):
        self.time_window = curses.newwin(2*curses.LINES/10, curses.COLS, 0, 0)
        self.time_window.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.time_window.refresh()
        self.time_window.nodelay(0)

        self.time_area = curses.newwin(2*curses.LINES/10 - 2, curses.COLS - 2, 1, 1)
        self.time_area.refresh()
        self.time_area.nodelay(0)
        
        self.current_time = time.strftime("%Y%m%d %H:%M:%S")
        self.time_area.addstr(1, 2, self.current_time)
        self.time_area.refresh()

    def paint(self):
        self.time_area.clear()
        self.time_area.addstr(1, 2, self.current_time)
        self.time_area.refresh()

    def run(self, semaphore):
        while(1):
            self.current_time = time.strftime("%Y%m%d %H:%M:%S")
            with semaphore:
                self.paint()


