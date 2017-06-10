"""This module servers web sockets"""
import SocketServer

class SimpleWebServer():
    """Server a websocket"""
    httpd = None
    websocketclass = None

    def __init__(self, host, port, handler, delay, wsport):
        """
        Args:
            host (str): The IP address for the websockets
            port (int): The port for the websockets
            handler (SocketHandler): The handler for the communication over websockets
        Returns:
            None
        """

        self.websocketclass = handler
        SocketServer.TCPServer.allow_reuse_address = True
        self.httpd = SocketServer.TCPServer((host, port), self.websocketclass)
        self.httpd.myhost = host
        self.httpd.delay = delay
        self.httpd.myport = wsport

    def serveforever(self):
        """Initialize Websockets Server"""
        self.httpd.serve_forever()

    def close(self):
        """Terminate Websockets Server"""
        self.httpd.server_close()
