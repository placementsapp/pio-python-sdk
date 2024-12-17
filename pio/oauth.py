import http.server
import socketserver
import urllib.parse
import webbrowser
import logging
import datetime
import httpx
import time
from pio.model.environment import API
from pio.model.oauth import ModelScopes
from pio.pio import PlacementsIO

OAUTH_RESPONSE = None


class OAuthMiniServer(http.server.SimpleHTTPRequestHandler):  # pragma: no cover
    def do_GET(self):
        # Parse the query parameters
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Extract the token code from the query parameters
        global OAUTH_RESPONSE  # pylint: disable=global-statement
        OAUTH_RESPONSE = query_params.get("code", [None])[0]
        logging.debug("Received OAuth token code", OAUTH_RESPONSE)

        # Respond to the client
        if OAUTH_RESPONSE:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"OAuth redirect received! You may now close this window.")
        else:
            error = query_params.get("error", ["OAuth authentication failed."])[0]
            error_description = query_params.get(
                "error_description", ["Please try again."]
            )[0]
            self.send_response(401)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
                {error}<br>
                {error_description}<br>
                <br>
                <a href='javascript:history.go(-1)'>Try again</a>
                """.encode()
            )


class PlacementsIO_OAuth(PlacementsIO):
    def __init__(
        self,
        environment: str = None,
        application_id: str = None,
        client_secret: str = None,
        redirect_host: str = "http://localhost",
        redirect_port: int = 17927,
        scopes: ModelScopes = None,
    ):
        self.base_url = API[environment]
        self.oauth_base_url = self.base_url.replace("/v1/", "/oauth/")
        self.application_id = application_id
        self.client_secret = client_secret
        self.redirect_host = redirect_host
        self.redirect_port = redirect_port
        self._oauth = {
            "access_token": None,
            "expires_in": 0,
            "refresh_token": None,
        }
        self._oauth_expiry = None
        self._set_oauth_expiry_time()
        scopes_param = f"&scope={"+".join(scopes or [])}" if scopes else ""
        self.auth_url = (
            f"{self.oauth_base_url}authorize"
            f"?client_id={self.application_id}"
            f"&redirect_uri={self.redirect_host}:{self.redirect_port}"
            f"&response_type=code{scopes_param}"
        )
        self.settings = {
            "base_url": self.base_url,
            "token": self.token,
        }
        self.logger = logging.getLogger("pio")

    def get_auth_url(self):
        return self.auth_url

    def get_user_auth(self):
        with socketserver.TCPServer(("", self.redirect_port), OAuthMiniServer) as httpd:
            print("Opening browser to authenticate...")
            print(f"\t{self.auth_url}")
            webbrowser.open(self.auth_url)
            print(
                f"Waiting for OAuth response on {self.redirect_host}:{self.redirect_port}"
            )
            print("\tPress Ctrl+C to cancel.")
            httpd.handle_request()
            while OAUTH_RESPONSE is None:
                time.sleep(1)
        return self.set_user_auth(OAUTH_RESPONSE)

    def set_user_auth(self, auth_code):
        self._fetch_access_token(auth_code)

    def token(self):
        if (
            datetime.datetime.now() > self._oauth_expiry
            and self._oauth.get("refresh_token") is not None
        ):
            self.logger.debug("Refreshing access token with refresh token")
            self._fetch_access_token(
                self._oauth.get("refresh_token"), grant="refresh_token"
            )
        elif self._oauth.get("access_token") is None:
            self.get_user_auth()
        return self._oauth.get("access_token")

    def _set_oauth_expiry_time(self, seconds=0):
        self._oauth_expiry = datetime.datetime.now() + datetime.timedelta(
            seconds=seconds
        )

    def _fetch_access_token(self, auth_code, grant: str = "authorization_code"):
        field_name = "code" if grant == "authorization_code" else grant
        response = httpx.post(
            url=f"{self.oauth_base_url}token",
            data={
                "client_id": self.application_id,
                "client_secret": self.client_secret,
                "redirect_uri": f"{self.redirect_host}:{self.redirect_port}",
                "grant_type": grant,
                field_name: auth_code,
            },
        )
        self._oauth = response.json()
        self._set_oauth_expiry_time(self._oauth.get("expires_in"))
