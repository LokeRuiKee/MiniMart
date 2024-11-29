from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    port = 8081  # Change this to your preferred port
    httpd = HTTPServer(('0.0.0.0', port), CORSRequestHandler)
    print(f"Serving on port {port} with CORS enabled")
    httpd.serve_forever()
