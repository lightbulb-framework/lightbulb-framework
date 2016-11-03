"""This module handles browser content"""
import SimpleHTTPServer
from urlparse import urlparse, parse_qs
from urllib import  unquote

class WebServerIframeHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """This class handles browser content"""
    delay = 50
    myport = 0
    myhost = "localhost"



    def log_message(self, format, *args):
        # sys.stderr.write("%input_string - - [%input_string] %input_string\n" %
        #                  (self.address_string(),
        #                   self.log_date_time_string(),
        #                   format%args))
        pass

    def do_GET(self):
        if "frame" in self.path:
            parsedParams = urlparse(self.path).query
            if len(parsedParams)>3:
                param = unquote(parsedParams[2:]).decode('utf8')
            else:
                param = ""

            mypage = """
                        <script>
                            var start = 0;
                            var myParent = window.top;
                            if (window.parent != window.top) {
                                myParent = window.parent;

                            }
                            window.onerror = function(msg, url) {
                                                 return true;
                                            };
                            function a(){
                                console.log('sending 0');
                                myParent.postMessage('0', '*');
                                start =1;
                            }
                        </script>
                        """ + param + """
                        <div>
                            <script>
                            y = 0;
                            (function wait() {
                                if ( y ) {
                                    if(start==0){
                                        console.log('sending 1');
                                        window.top.postMessage('1', '*');
                                    }
                                } else {
                                     y =  y+1;
                                    setTimeout( wait, """ + `self.delay` + """ );
                                }
                            })();
                            </script>
                        </div>
                        """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(mypage))
            self.end_headers()
            self.wfile.write(mypage)

        else:
            mypage = """
            <title>Fingerprint Test</title>
                <head>
                <script language="javascript" type="text/javascript">
                if (!window.location.origin) {
                  window.location.origin = window.location.protocol + "//" + window.location.hostname + (window.location.port ? ':' + window.location.port: '');
                }
                window.origin = window.location.origin;
                  x = 1;
                  function b64DecodeUnicode(str) {
                    return decodeURIComponent(Array.prototype.map.call(atob(str), function(c) {
                    return '%' + c.charCodeAt(0).toString(16);
                    }).join(''));
                  }

                  function doConnect()
                  {
                    websocket = new WebSocket("ws://""" + self.myhost + """:""" + `self.myport` + """/");
                    websocket.onopen = function(evt) { websocket.send("INIT"); };
                    websocket.onmessage = function(evt) { onMessage(evt) };
                  }

                  function b64DecodeUnicode(str) {
                    return decodeURIComponent(Array.prototype.map.call(atob(str), function(c) {
                    return '%' + c.charCodeAt(0).toString(16);
                    }).join(''));
                  }

                  window.addEventListener( "message",
                  function (e) {
                        console.log('message Received');
                      x = e.data;
                      console.log(x);websocket.send(x);
                      x = 1;
                  },
                  false);

                   function onMessage(evt)
                   {

                      var text ='';
                      if (evt.data instanceof Blob){
                        var reader = new FileReader();
                        reader.addEventListener("loadend", function() {
                            text=b64DecodeUnicode(reader.result);
                            writeToScreen(text);
                        });
                        reader.readAsText(evt.data);
                      }else{
                        text=b64DecodeUnicode(reader.result);
                        writeToScreen(text);
                      }

                  }

                  function writeToScreen(message)
                  {
                    x = 1;
                    document.getElementById("output").src="frame?c="+encodeURIComponent(message);
                    console.log(message);
                    var el =  document.getElementById("output").childNodes;
                    if (el.length>1){
                        for (var k in el){
                          if (el[k] instanceof HTMLElement || el[k].nodeType > 0){
                            if ("onclick" in el[k]){
                              el[k].click();
                            }
                          }
                      }
                    }

                  }
                </script>
                </head>
                <body onload="doConnect();">
                    <iframe id="output" src='' value='0'>
                </body>
                </html>
                """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(mypage))
            self.end_headers()
            self.wfile.write(mypage)
