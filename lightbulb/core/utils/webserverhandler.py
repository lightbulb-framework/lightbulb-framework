"""This module handles browser content"""
import SimpleHTTPServer


class WebServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """This class handles browser content"""

    def log_message(self, format, *args):
        # sys.stderr.write("%input_string - - [%input_string] %input_string\n" %
        #                  (self.address_string(),
        #                   self.log_date_time_string(),
        #                   format%args))
        pass

    def do_GET(self):
        mypage = """
            <title>Fingerprint Test</title>
            <head>
            <script language="javascript" type="text/javascript">
              var x = 1;
              var changed = 0;

              window.onerror = function(msg, url) {
                 console.log(msg);
                 if (msg.indexOf(" a is not a function") !=-1) {
                      x = 0;
                 }
                 changed = 1;
                 return true;
              };

              function hexdecoder(hex) {
                var str = '';
                for (var i = 0; i < hex.length; i += 2){
                  str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
                }
                return str;
              }
               var waitUntil = function (fn, condition, interval) {
                  interval = interval || 100;

                  var shell = function () {
                          var timer = setInterval(
                              function () {
                                  var check;

                                  try { check = !!(condition()); } catch (e) { check = false; }

                                  if (check) {
                                      clearInterval(timer);
                                      delete timer;
                                      fn();
                                  }
                              },
                              interval
                          );
                      };

                  return shell;
              };
              function doConnect()
              {
                websocket = new WebSocket("ws://""" + self.server.myhost + """:""" + `self.server.myport` + """/");
                websocket.onopen = function(evt) { websocket.send("INIT"); };
                websocket.onmessage = function(evt) { onMessage(evt) };
              }
    
              function onMessage(evt)
              {
                var text ='';
                if (evt.data instanceof Blob){
                  var reader = new FileReader();
                  reader.addEventListener("loadend", function() {
                      text=hexdecoder(reader.result); 
                      writeToScreen(text);
                  });
                  reader.readAsText(evt.data);
                }else{
                  text=hexdecoder(reader.result); 
                  writeToScreen(text);
                }
              }

              function a(){
                x=0;
              }

         function writeToScreen(message)
              {
                document.getElementById("output").innerHTML = "";
                x=1;
                changed=0;
                var vector = message;
                document.getElementById("output").innerHTML = "<img src=# onerror='changed=1'>"+vector;
                console.log(vector);
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
                waitUntil(
                  function () {
                    y = 0;
                    (function wait() {
                        if ( y ) {
                            console.log(x);websocket.send(x);
                        } else {
                             y =  y+1;
                            setTimeout( wait, """ + `self.server.delay` + """ );
                        }
                    })();
                  },
                  function() {
                    return (changed==1);
                  },
                  10
                )();
              }
            </script>
            </head>
            <body onload="doConnect();">
            <div id="output" ></div>
            </body>
            </html> 
            """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(mypage))
        self.end_headers()
        self.wfile.write(mypage)
