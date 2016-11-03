"""This module manages browser communication through web sockets"""
from SimpleWebSocketServer import WebSocket


class SocketHandler(WebSocket):
    """This class manages browser communication through web sockets"""
    conn = None
    parentconn = None
    myport = 0

    def handleMessage(self):
        """
        Send a message though websockets.
        """
        self.conn.send(['browserresponse', self.data])
        updates = self.conn.recv()
        if updates[0] == "serverrequest":
            self.sendMessage(updates[1])

    def handleConnected(self):
        """Browser was connected"""
        self.conn.send(['browserstatus', 1])

    def handleClose(self):
        """Browser was disconnected"""
        self.conn.send(['browserstatus', 0])
