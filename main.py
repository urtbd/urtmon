import curses
import math
import socket
import sys
import time
from threading import Timer


class UrTop:
    def __init__(self):
        self.screen = curses.initscr()
        self.max_yx = self.screen.getmaxyx()
        self.name_length = int(math.floor(self.max_yx[1] * 0.50))
        self.score_length = self.ping_length = int(math.floor(self.max_yx[1] * 0.25))
        self.title_start = int(math.floor(self.max_yx[1] * 0.40))

        self.host = "5.135.165.34"
        self.port = "27001"
        self.server_details = None
        self.get_server_details()

        curses.nocbreak()
        curses.noecho()

    def update_view(self):
        self.get_server_details()
        self.paint_layout()


    def get_server_details(self):
        # Data Place Holders
        urt_server_details = {}

        # Socket Request Message
        MESSAGE = "\377\377\377\377getstatus"

        # Get response from server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((self.host, int(self.port)))
            sock.send(MESSAGE)
            response, addr = sock.recvfrom(1024)
            sock.close()
            response_lines = response.split("\n")
        except Exception, exc:
            print "The connection to the server failed. Did you provide the correct hostname and port?"
            print "Error message for the Geeks: " + str(exc)
            sys.exit(2)

        # Retrieve the server settings
        config_string_parts = response_lines[1].split("\\")
        urt_server_details['configs'] = {}
        for i in range(1, len(config_string_parts), 2):
            urt_server_details['configs'][config_string_parts[i].strip()] = config_string_parts[i + 1].strip()

        urt_server_details['players'] = []
        for x in range(2, (len(response_lines) - 1)):
            player_data = response_lines[x].split(" ")
            player_dictionary = {"ping": player_data[1], "score": player_data[0], "name": player_data[2][1:-1]}
            urt_server_details['players'].append(player_dictionary)

        self.server_details = urt_server_details

    def paint_layout(self):
        self.screen.clear()
        self.screen.addstr(0, self.title_start, "UrT Server Monitor")
        self.screen.hline(1, self.title_start, '=', 20)
        self.screen.addstr(4, 0, "Player")
        self.screen.hline(5, 0, '-', 10)
        self.screen.addstr(4, self.name_length + 1, "Score")
        self.screen.hline(5, self.name_length + 1, '-', 10)
        self.screen.addstr(4, self.name_length + 1 + self.score_length + 1, "Ping")
        self.screen.hline(5, self.name_length + 1 + self.score_length + 1, '-', 10)

        y = 6
        for player in self.server_details['players']:
            self.screen.addnstr(y, 0, player['name'], self.name_length)
            self.screen.addnstr(y, self.name_length + 1, player['score'], self.score_length)
            self.screen.addnstr(y, self.name_length + 1 + self.score_length + 1, player['ping'], self.ping_length)

            y += 1

        self.screen.refresh()


class TimedRunner():
    def __init__(self, interval, func):
        self.time_interval = interval
        self.func = func
        self.thread = Timer(self.time_interval, self.handle_function)

    def handle_function(self):
        self.func()
        self.thread = Timer(self.time_interval, self.handle_function)
        self.thread.start()


    def start(self):
        self.func()
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def main():
    urtop.update_view()
    time.sleep(1)


urtop = UrTop()

runner = TimedRunner(2, main)
runner.start()








