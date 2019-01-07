from abc import ABC, abstractmethod
from http.cookies import SimpleCookie, CookieError
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

from google.auth.transport import requests
from google.oauth2 import id_token

PAGE = """\
<html>
    <head>
        <title>Puppy Cam</title>
        
        <meta name="google-signin-scope" content="profile email">
        <meta name="google-signin-client_id" content="%s">
        
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
            document.cookie = "token=" + id_token;
            
            document.getElementById("stream").innerHTML = '<img src="/stream.mjpg"/>';
            document.getElementById("login").toggleAttribute("hidden");
            document.getElementById("logout").toggleAttribute("hidden");
          }
        </script>
    </body>
</html>
"""


class BaseStreamingHandler(BaseHTTPRequestHandler, ABC):
    def do_GET(self):
        url = urlparse(self.path)

        if url.path == '/':
            self.redirect_root()
        elif url.path == '/index.html':
            self.index()
        elif url.path == '/stream.mjpg':
            self.stream(url)
        else:
            self.not_found()

    def stream(self, url):
        try:
            parameters = parse_qs(url.query)

            cookie = SimpleCookie()
            cookie.load(self.headers["Cookie"])

            token = cookie["token"].value

            user = id_token.verify_oauth2_token(token, requests.Request(), self.server.client_id)

            if user['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            if user["email"] not in self.server.users:
                raise ValueError("Invalid user '%s'." % user["email"])

            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            self.send_frames()
        except (ValueError, CookieError) as e:
            print("Invalid log in attempt.", e)

            self.send_error(401)
            self.end_headers()

    def not_found(self):
        self.send_error(404)
        self.end_headers()

    def index(self):
        body = (PAGE % self.server.client_id).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def redirect_root(self):
        self.send_response(301)
        self.send_header('Location', '/index.html')
        self.end_headers()

    @abstractmethod
    def send_frames(self):
        pass


class StreamingServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, frames, client_id, users, server_address, handler_class):
        self.frames = frames
        self.client_id = client_id
        self.users = users
        super().__init__(server_address, handler_class)
