import curses
import math
import socket
import sys
from threading import Thread
from Queue import Queue
from time import sleep

HOST = "5.135.165.34"
PORT = "27001"

queue = Queue()


class UrTMon:
    def __init__(self, host, port):
        self.screen = curses.initscr()
        self.max_yx = self.screen.getmaxyx()

        # 3 columns, 50%, 25% 25% of current width
        self.name_length = int(math.floor(self.max_yx[1] * 0.50))
        self.score_length = self.ping_length = int(math.floor(self.max_yx[1] * 0.25))
        self.title_start = int(math.floor(self.max_yx[1] * 0.40))

        # Test host
        self.host = host
        self.port = port

        # Start with the server details
        self.server_details = None

        # Don't echo, don't break on character input
        curses.nocbreak()
        curses.noecho()

    def update_view(self):
        self.get_server_details()
        self.paint_layout()

    # function shamelessly borrowed from pyurtstat project
    # Source: https://github.com/masnun/pyurtstat/blob/master/pyurtstat.py
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
        # Clear the screen, just to be sure
        self.screen.clear()

        # Title message
        self.screen.addstr(0, self.title_start, "UrT Server Monitor")
        self.screen.hline(1, self.title_start, '=', 20)

        # Top row
        self.screen.addstr(4, 0, "Player")
        self.screen.hline(5, 0, '-', 10)
        self.screen.addstr(4, self.name_length + 1, "Score")
        self.screen.hline(5, self.name_length + 1, '-', 10)
        self.screen.addstr(4, self.name_length + 1 + self.score_length + 1, "Ping")
        self.screen.hline(5, self.name_length + 1 + self.score_length + 1, '-', 10)

        # Display the player information
        y = 6
        for player in self.server_details['players']:
            self.screen.addnstr(y, 0, player['name'], self.name_length)
            self.screen.addnstr(y, self.name_length + 1, player['score'], self.score_length)
            self.screen.addnstr(y, self.name_length + 1 + self.score_length + 1, player['ping'], self.ping_length)

            y += 1

        # Done writing, repaint the screen
        self.screen.refresh()


class Worker(Thread):
    def __init__(self, urtmon, queue):
        Thread.__init__(self)


        self.queue = queue
        self.urtmon = urtmon
        self.setDaemon(True)


    def run(self):
        while True:
            self.queue.get()
            self.urtmon.update_view()


if __name__ == "__main__":
    # Global variable which is accessible from above func
    urtmon = UrTMon(HOST,PORT)
    worker = Worker(urtmon, queue)
    worker.start()

    try:
        while True:
            queue.put(True)
            sleep(3)
    except KeyboardInterrupt:
        curses.endwin()
        sys.exit()










