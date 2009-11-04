# -*- coding: utf-8 -*-

import curses
import time

class ClockModule(object):
    def __init__(self, method_list=None):
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

        self.method_list = method_list

    def paint(self):
        self.time_area.clear()
        self.time_area.addstr(1, 2, self.current_time)
        self.time_area.refresh()

    def run(self, semaphore):
        while(True):
            self.current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            with semaphore:
                self.paint()
            time.sleep(1)
            for method in self.method_list:
                if callable(method):
                    method()
        