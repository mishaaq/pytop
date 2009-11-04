# -*- coding: utf-8 -*-

import os
import re
import curses
import operator
import traceback
import copy

class ProcessStatus(object):
    def __init__(self):
        self.pid = None
        self.name = None
        self.command = None
        self.state = None
        self.utime = 0
        self.uperc = 0
        self.stime = 0
        self.sperc = 0
        self.nice = None
        self.mem = None

class ProcessesModule(object):
    def __init__(self, method_list=None):
        self.window_rect_dict = {}
        self.window_rect_dict['list_window'] = [8*curses.LINES/10, curses.COLS/2, 2*curses.LINES/10, 0]
        self.window_rect_dict['list_area'] = [8*curses.LINES/10 - 2, curses.COLS/2 - 2, 2*curses.LINES/10 + 1, 1]
        self.window_rect_dict['desc_window'] = [8*curses.LINES/10, curses.COLS/2, 2*curses.LINES/10, curses.COLS/2]
        self.window_rect_dict['desc_area'] = [8*curses.LINES/10 - 2, curses.COLS/2 - 2, 2*curses.LINES/10 + 1, curses.COLS/2 + 1]

        self.list_window = curses.newwin(self.window_rect_dict['list_window'][0],
                                         self.window_rect_dict['list_window'][1],
                                         self.window_rect_dict['list_window'][2],
                                         self.window_rect_dict['list_window'][3])
        self.list_window.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.list_window.refresh()
        self.list_window.nodelay(0)

        self.list_area = curses.newwin(self.window_rect_dict['list_area'][0],
                                       self.window_rect_dict['list_area'][1],
                                       self.window_rect_dict['list_area'][2],
                                       self.window_rect_dict['list_area'][3])
        self.list_area.refresh()
        self.list_area.nodelay(0)

        self.desc_window = curses.newwin(self.window_rect_dict['desc_window'][0],
                                         self.window_rect_dict['desc_window'][1],
                                         self.window_rect_dict['desc_window'][2],
                                         self.window_rect_dict['desc_window'][3])
        self.desc_window.box(curses.ACS_VLINE, curses.ACS_HLINE)
        self.desc_window.refresh()
        self.desc_window.nodelay(0)

        self.desc_area = curses.newwin(self.window_rect_dict['desc_area'][0],
                                       self.window_rect_dict['desc_area'][1],
                                       self.window_rect_dict['desc_area'][2],
                                       self.window_rect_dict['desc_area'][3])
        self.desc_area.refresh()
        self.desc_area.nodelay(0)

        self.highlighted_line = 0
        self.first_line_to_paint = 0

        # lista informacji o procesach w systemie
        self.status_list = []

        # wyrażenie regułowe testujące nazwy katalogów (przechodzą katalogi-pidy)
        self.directory_pattern = re.compile(r'\d+')

        # określa, po czym była ostatnio sortowana lista
        self.last_sort = 'pid'
        self.reverse = False

        self.freeze = False
        
        self.refresh_processes()

    def refresh_processes(self):
        if self.freeze:
            return
        old_status_list = copy.deepcopy(self.status_list)
        del self.status_list[:]
        for entry in os.listdir('/proc/'):
            if self.directory_pattern.match(entry):
                base_file_name = '/proc/' + entry
                try:
                    status = ProcessStatus()
                    with open(base_file_name + '/stat') as file:
                        data = file.readline().split()
                        status.pid = int(data[0])
                        status.command = data[1]
                        status.state = data[2]
                        status.utime = float(data[13])
                        status.stime = float(data[14])
                        status.nice = data[18]
                    with open(base_file_name + '/statm') as file:
                        data = file.readline().split()
                        status.mem = data[0]
                    with open(base_file_name + '/status') as file:
                        data = file.readline().split()
                        status.name = data[1]
                    try:
                        old_status = (stat for stat in old_status_list if stat.name == status.name).next()
                        status.uperc = status.utime - old_status.utime
                        status.sperc = status.stime - old_status.stime
                    except StopIteration:
                        status.uperc = 0.0
                        status.sperc = 0.0
                    self.status_list.append(status)
                except IOError:
                    pass
        self.sort_list()
        
    def paint(self):
        self.list_area.clear()
        max_lines = self.window_rect_dict['list_area'][0]
        last_line_to_paint = self.first_line_to_paint + max_lines
        processes_to_paint = self.status_list[self.first_line_to_paint:last_line_to_paint]
        for current_row, process in enumerate(processes_to_paint):
            name = process.name
            if current_row == self.highlighted_line:
                self.list_area.addstr(current_row, 0, name[:self.window_rect_dict['list_area'][1]], curses.A_BOLD)
            else:
                self.list_area.addstr(current_row, 0, name[:self.window_rect_dict['list_area'][1]])

        self.desc_area.clear()
        self.desc_area.addstr(0, 0, 'PID: %d' % self.status_list[self.first_line_to_paint+self.highlighted_line].pid)
        self.desc_area.addstr(1, 0, 'NAME: ' + self.status_list[self.first_line_to_paint+self.highlighted_line].name)
        self.desc_area.addstr(2, 0, 'COMM: ' + self.status_list[self.first_line_to_paint+self.highlighted_line].command)
        self.desc_area.addstr(3, 0, 'STATE: ' + self.status_list[self.first_line_to_paint+self.highlighted_line].state)
        self.desc_area.addstr(4, 0, 'UTIME: %3.1f %%' % self.status_list[self.first_line_to_paint+self.highlighted_line].uperc)
        self.desc_area.addstr(5, 0, 'STIME: %3.1f %%' % self.status_list[self.first_line_to_paint+self.highlighted_line].sperc)
        self.desc_area.addstr(6, 0, 'NICE: ' + self.status_list[self.first_line_to_paint+self.highlighted_line].nice)
        self.desc_area.addstr(7, 0, 'MEM: ' + self.status_list[self.first_line_to_paint+self.highlighted_line].mem + ' kB')
        self.desc_area.refresh()

        self.list_area.refresh()
    
    def move_highlight(self, lines):
        if self.last_sort in ['uperc', 'sperc'] and not self.freeze:
            return
        if lines < 0:
            if self.highlighted_line == 0:
                self.first_line_to_paint += lines
                if self.first_line_to_paint < 0:
                    self.first_line_to_paint = 0
            else:
                self.highlighted_line -= 1
        else:
            if self.highlighted_line == self.window_rect_dict['list_area'][0] - 1:
                self.first_line_to_paint += lines
                if self.first_line_to_paint + self.window_rect_dict['list_area'][0] > len(self.status_list):
                    self.first_line_to_paint = len(self.status_list) - self.window_rect_dict['list_area'][0]
            else:
                self.highlighted_line += 1

    def sort_list(self, by=None):
        if not by:
            by = self.last_sort
        else:
            if by == self.last_sort:
                self.reverse = not self.reverse
            else:
                self.reverse = False
        self.status_list.sort(key=operator.attrgetter(by), reverse=self.reverse)
        self.last_sort = by

    def run(self, semaphore):
        try:
            while True:
                with semaphore:
                    self.paint()
                try:
                    char = self.list_area.getkey()
                    {'i': lambda: self.move_highlight(-1),
                     'k': lambda: self.move_highlight(1),
                     '1': lambda: self.sort_list('pid'),
                     '2': lambda: self.sort_list('name'),
                     '3': lambda: self.sort_list('command'),
                     '4': lambda: self.sort_list('state'),
                     '5': lambda: self.sort_list('uperc'),
                     '6': lambda: self.sort_list('stime'),
                     '7': lambda: self.sort_list('nice'),
                     '8': lambda: self.sort_list('mem'),
                    }[char]()
                except KeyError:
                    pass
                if char == 'q':
                    break
                if char == 'f':
                    self.freeze = not self.freeze
        except:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            traceback.print_exc()
