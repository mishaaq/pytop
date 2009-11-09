#!/usr/bin/env python
# -*- coding: utf-8 -*-


import curses
import sys
from threading import Thread
from threading import Semaphore

from processes_module import ProcessesModule
from clock_module import ClockModule

painting_semaphore = Semaphore(value=1)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        proc_mod = ProcessesModule(semaphore=painting_semaphore)
        clock_mod = ClockModule(semaphore=painting_semaphore, method_list=(proc_mod.refresh_processes,))

        proc_mod_process = Thread(target = proc_mod.run)
        clock_mod_process = Thread(target = clock_mod.run)
        proc_mod_process.start()
        clock_mod_process.start()

        proc_mod_process.join()
    finally:
        curses.nocbreak()
        curses.echo()
        stdscr.keypad(0)
        curses.endwin()

if __name__ == "__main__":
    sys.exit(main())
