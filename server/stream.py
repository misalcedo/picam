from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = """\
<html>
    <head>
        <title>Puppy Cam</title>
        
        <meta name="google-signin-scope" content="profile email">
        <meta name="google-signin-client_id" content="652926339660-fj2ufv0cntljjf692e7h0v9in1nn020l.apps.googleusercontent.com">
        
        <script src="https://apis.google.com/js/platform.js" async defer></script>
    </head>
    <body>
        <h1>Puppy Cam</h1>

        <div id="stream"></div>
        <div id="login" class="g-signin2" data-onsuccess="onSignIn" data-theme="dark"></div>
        <button id="logout" hidden=true onclick="signOut();">Sign out</button>
        
        <script>
          function signOut(e) {
            var auth2 = gapi.auth2.getAuthInstance();
            auth2.signOut().then(function () {
              console.log('User signed out.');
              
              window.location.href = "/";
            });
          }
          
          function onSignIn(googleUser) {
            // Useful data for your client-side scripts:
            var profile = googleUser.getBasicProfile();
            
            console.log("ID: " + profile.getId()); // Don't send this directly to your server!
            console.log('Full Name: ' + profile.getName());
            console.log('Given Name: ' + profile.getGivenName());
            console.log('Family Name: ' + profile.getFamilyName());
            console.log("Image URL: " + profile.getImageUrl());
            console.log("Email: " + profile.getEmail());
                
            // The ID token you need to pass to your backend:
            var id_token = googleUser.getAuthResponse().id_token;
            console.log("ID Token: " + id_token);
            
            document.getElementById("stream").innerHTML = '<img src="stream.mjpg"/>';
            document.getElementById("login").toggleAttribute("hidden");
            document.getElementById("logout").toggleAttribute("hidden");
          }
        </script>
    </body>
</html>
""".encode('utf-8')


class BaseStreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.redirect_root()
        elif self.path == '/index.html':
            self.index()
        elif self.path == '/stream.mjpg':
            self.stream()
        else:
            self.not_found()

    def stream(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        self.send_frames()

    def not_found(self):
        self.send_error(404)
        self.end_headers()

    def index(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(PAGE))
        self.end_headers()
        self.wfile.write(PAGE)

    def redirect_root(self):
        self.send_response(301)
        self.send_header('Location', '/index.html')
        self.end_headers()


class StreamingServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, frames, server_address, handler_class):
        self.frames = frames
        super().__init__(server_address, handler_class)
