# -*- coding: utf-8 -*-

import curses
import time

class ClockModule(object):
    def __init__(self, semaphore, method_list=None):
        self.time_window = curses.newwin(2*curses.LINES/10, curses.COLS, 0, 0)
        self.time_window.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.time_window.refresh()
        self.time_window.nodelay(0)

        self.time_area = curses.newwin(2*curses.LINES/10 - 2, curses.COLS - 2, 1, 1)
        self.time_area.refresh()
        self.time_area.nodelay(1)
        
        self.current_time = time.strftime("%Y%m%d %H:%M:%S")
        self.time_area.addstr(1, 2, self.current_time)
        self.time_area.refresh()

        self.method_list = method_list

        self.semaphore = semaphore

    def paint(self):
        self.semaphore.acquire()
        self.time_area.clear()
        self.time_area.addstr(1, 2, self.current_time)
        self.time_area.refresh()
        self.semaphore.release()

    def run(self):
        while(True):
            self.current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.paint()
            for method in self.method_list:
                if callable(method):
                    method()
            time.sleep(1)
        