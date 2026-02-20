import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import shutil

UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class UploadHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
        <html>
        <body>
        <h2>Upload File</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file"/>
            <input type="submit" value="Upload"/>
        </form>
        </body>
        </html>
        """)

    def do_POST(self):
        content_type = self.headers.get('Content-Type')
        if not content_type:
            self.send_error(400, "No Content-Type header")
            return

        boundary = content_type.split("boundary=")[-1].encode()
        remainbytes = int(self.headers['Content-Length'])

        line = self.rfile.readline()
        remainbytes -= len(line)

        if boundary not in line:
            self.send_error(400, "Content does not begin with boundary")
            return

        line = self.rfile.readline()
        remainbytes -= len(line)

        filename = line.decode().split("filename=")[-1].strip().strip('"')
        filepath = os.path.join(UPLOAD_DIR, os.path.basename(filename))

        # Skip Content-Type line
        self.rfile.readline()
        self.rfile.readline()
        remainbytes -= len(line) * 2

        with open(filepath, "wb") as out_file:
            preline = self.rfile.readline()
            remainbytes -= len(preline)

            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if boundary in line:
                    out_file.write(preline.rstrip(b"\r\n"))
                    break
                else:
                    out_file.write(preline)
                    preline = line

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"File uploaded successfully!")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), UploadHandler)
    print("Server running on http://0.0.0.0:8000")
    server.serve_forever()
