'''Author: Andrew Seligman 
Date: 10.3.18
This program is a client to network_detector.py. It creates a GTK StatusIcon
to show a simplified status of the LEDs controlled by the server. Network
activity is delegated to a thread to allow for possible updates that make
use of a more detailed GUI.
Tested on Windows 7 using python 3.7
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import time, socket, threading

HOST = '10.0.0.8'
PORT = 24680
ICONS = {'grey': 'icons/grey.ico',
        'white': 'icons/white.ico',
        'green': 'icons/green.ico',
        'yellow': 'icons/yellow.ico',
        'red': 'icons/red.ico',
        }

class MessageThread(threading.Thread):
    '''Create a new thread to read network messages and update the StatusIcon
    '''
    def run(self):
        while True:
            #print("Creating new thread")
            self.connected = False
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((HOST, PORT))
                self.connected = True
            except TimeoutError:
                statusicon.set_tooltip_text("BeagleBone not found on network")
            except ConnectionRefusedError:
                statusicon.set_tooltip_text("Ammy detector program is not running")
            finally:
                statusicon.set_from_file(ICONS['grey'])
            
            self.first_message = True
            while self.connected:
                try:
                    if not self.first_message:
                        self.s.sendall(b"a")
                    else:
                        self.first_message = False
                    self.icon = self.s.recv(1024).decode("utf-8")
                    if not self.icon:
                        break
                    if self.icon == 'red':
                        self.message = "Ammy is waiting to come in"
                    elif self.icon == 'yellow':
                        self.message = "Ammy has been out for a while"
                    elif self.icon == 'green':
                        self.message = "Ammy is outside"
                    else:
                        self.message = "Ammy detector connected"
                    statusicon.set_from_file(ICONS[self.icon])
                    statusicon.set_tooltip_text(self.message)
                except:
                    statusicon.set_tooltip_text("Unspecified error occurred")
                    statusicon.set_from_file(ICONS['grey'])
                    self.connected = False
            self.s.close()
            #if connection drops, wait a bit before attempting to reconnect
            time.sleep(30)

# class MyWindow(Gtk.Window):
    # def __init__(self):
        # Gtk.Window.__init__(self, title="Hello World")
        # self.button = Gtk.Button(label="Ammy is waiting to come in")
        # self.button.connect("clicked", self.on_button_clicked)
        # self.add(self.button)

    # def on_button_clicked(self, widget):
        # Gtk.main_quit()

statusicon = Gtk.StatusIcon()
statusicon.set_from_file(ICONS['grey'])
statusicon.set_tooltip_text("Ammy detector disconnected")

MessageThread().start()

# win = MyWindow()
# win.connect("delete-event", Gtk.main_quit)
# win.show_all()
Gtk.main()
