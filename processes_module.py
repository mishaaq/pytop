# -*- coding: utf-8 -*-

import curses
import commands
import traceback

class StatusQuery(object):
    def __init__(self):
        self.pid = None
        self.command = None
        self.state = None
        self.utime = None
        self.stime = None
        self.nice = None
        self.mem = None

class ProcessesModule(object):
    def __init__(self, screen):
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
        self.query = StatusQuery()

        self.refresh_processes_list()

    def refresh_processes_list(self):
        self.processes_list = []
        processes_buffer = commands.getoutput('ps -A').splitlines()
        del processes_buffer[0]
        for line in processes_buffer:
            line = line.strip().split()
            self.processes_list.append((line[0], line[3]))

    def update_descriptions(self):
        pid = self.processes_list[self.highlighted_line + self.first_line_to_paint][0]
        file_name = '/proc/' + pid + '/stat'
        try:
            with open(file_name) as file:
                data = file.readline().split()
                self.query.pid = data[0]
                self.query.command = data[1]
                self.query.state = data[2]
                self.query.utime = float(data[13])
                self.query.stime = float(data[14])
                self.query.nice = data[18]
            with open(file_name + 'm') as file:
                data = file.readline().split()
                self.query.mem = data[0]
        except IOError:
            pass
        
    def paint(self):
        self.list_area.clear()
        max_lines = self.window_rect_dict['list_area'][0]
        last_line_to_paint = self.first_line_to_paint + max_lines
        processes_to_paint = self.processes_list[self.first_line_to_paint:last_line_to_paint]
        current_row = 0
        for process in processes_to_paint:
            name = process[1]
            if current_row == self.highlighted_line:
                self.list_area.addstr(current_row, 0, name[:self.window_rect_dict['list_area'][1]], curses.A_BOLD)
            else:
                self.list_area.addstr(current_row, 0, name[:self.window_rect_dict['list_area'][1]])
            current_row += 1

        self.desc_area.clear()
        self.desc_area.addstr(0, 0, 'PID: ' + self.query.pid)
        self.desc_area.addstr(1, 0, 'COMM: ' + self.query.command)
        self.desc_area.addstr(2, 0, 'STATE: ' + self.query.state)
        self.desc_area.addstr(3, 0, 'UTIME: %5f s' % (self.query.utime / 250.0))
        self.desc_area.addstr(4, 0, 'STIME: %5f s' % (self.query.stime / 250.0))
        self.desc_area.addstr(5, 0, 'NICE: ' + self.query.nice)
        self.desc_area.addstr(6, 0, 'MEM: ' + self.query.mem + ' kB')
        self.desc_area.refresh()

        self.list_area.refresh()
    
    def move_highlight(self, lines):
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
                if self.first_line_to_paint + self.window_rect_dict['list_area'][0] > len(self.processes_list):
                    self.first_line_to_paint = len(self.processes_list) - self.window_rect_dict['list_area'][0]
            else:
                self.highlighted_line += 1
    
    def run(self, semaphore):
        try:
            while True:
                self.update_descriptions()
                with semaphore:
                    self.paint()
                char = self.list_area.getkey()
                if char == 'q':
                    break;
                if char == 'i':
                    self.move_highlight(-1)
                if char == 'k':
                    self.move_highlight(1)
        except:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            traceback.print_exc()
