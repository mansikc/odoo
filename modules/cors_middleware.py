# cors_handler/cors_middleware.py

from odoo import http
from odoo.http import Response

# Backup the original dispatch method
_original_dispatch = http.Http.dispatch

def cors_enabled_dispatch(self, *args, **kwargs):
    # Call the original dispatch method
    response = _original_dispatch(self, *args, **kwargs)
    
    # If the response is not already an HTTP response, convert it
    if not isinstance(response, Response):
        response = Response(response)
    
    # Inject CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

# Replace the default dispatcher with the CORS-enabled one
http.Http.dispatch = cors_enabled_dispatch
