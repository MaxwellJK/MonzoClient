#!/usr/bin/env python
from flask import Flask, abort, request
from uuid import uuid4
import requests
import _thread
import wx
#import wx.html
import wx.html2
#import requests.auth
import urllib
CLIENT_ID = "oauthclient_00009Qs5klehAJyGUjKdjF"
CLIENT_SECRET = "JSkQ7mxVXwEJUgf0gAe0dcH9nZFEHyL+f1GxQlWs2yRK8heHWGy40FbOZ3WHrvZk/8qu/c09UydmTkM+QsAf"
REDIRECT_URI = "http://localhost:65010/monzo_callback"

'''class MyBrowser(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        self._url = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._url.SetHint("Enter URL here and press enter...")
        back = wx.Button(self, style=wx.BU_EXACTFIT)
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR)
        fw = wx.Button(self, style=wx.BU_EXACTFIT)
        fw.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(fw, 0, wx.ALL, 5)
        sizer.Add(self.url, 1, wx.EXPAND)
        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize((700, 700))
'''
class NaviBar(wx.Panel):
    def __init__(self, parent, browser):
        super(NaviBar, self).__init__(parent)
        self._url = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._url.SetHint("Enter URL here and press enter...")
        back = wx.Button(self, style=wx.BU_EXACTFIT)
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR)
        fw = wx.Button(self, style=wx.BU_EXACTFIT)
        fw.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(fw, 0, wx.ALL, 5)
        sizer.Add(self._url, 1, wx.EXPAND)
        self.SetSizer(sizer)
        b = browser
        self.Bind(wx.EVT_TEXT_ENTER, lambda event: b.LoadURL(self._url.Value))
        self.Bind(wx.EVT_BUTTON, lambda event: b.GoBack(), back)
        self.Bind(wx.EVT_BUTTON, lambda event: b.GoForward(), fw)
        self.Bind(wx.EVT_UPDATE_UI, lambda event: event.Enable(b.CanGoBack()), back)
        self.Bind(wx.EVT_UPDATE_UI, lambda event: event.Enable(b.CanGoForward()), fw)

class WebFrame(wx.Frame):
    def __init__(self, parent, title):
        super(WebFrame, self).__init__(parent, title=title)
        self._browser = wx.html2.WebView.New(self)
        self._browser.LoadURL("http://127.0.0.1:65010")
        self._bar = NaviBar(self, self._browser)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._bar, 0, wx.EXPAND)
        sizer.Add(self._browser, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetSize((700, 700))
        self.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.OnTitle)
        
    def OnTitle(self, event):
        self.Title = event.GetString()

def user_agent():
    '''reddit API clients should each have their own, unique user-agent
    Ideally, with contact info included.
    
    e.g.,
    return "oauth2-sample-app by /u/%s" % your_reddit_username
    '''
    raise NotImplementedError()

def base_headers():
    return {"User-Agent": user_agent()}


app = Flask(__name__)
@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with Monzo</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    #save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI}
    url = "https://auth.getmondo.co.uk/?" + urllib.parse.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass
def is_valid_state(state):
    return True

@app.route('/monzo_callback')
def monzo_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    params = {"grant_type": "authorization_code",
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "redirect_uri": REDIRECT_URI,
              "code": code}
    url = "https://api.monzo.com/oauth2/token"
    response = requests.post(url, params)
    access_token = response['access_token']
    client_id = response['client_id']
    expires_in = response['expires_in']
    refresh_token = response['refresh_token']
    token_type = response['token_type']
    user_id = response['user_id']
    return "You have been authorized. You can close the web browser and carry on with DeskApp."

#def get_token(code):
    #client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    #post_data = {"grant_type": "authorization_code",
    #             "code": code,
    #             "redirect_uri": REDIRECT_URI}
    #headers = base_headers()
    #response = requests.post("https://ssl.reddit.com/api/v1/access_token",
    #                         auth=client_auth,
    #                         headers=headers,
    #                         data=post_data)
    #token_json = response.json()
    #return token_json["access_token"]
    
    
def get_username(access_token):
    headers = base_headers()
    headers.update({"Authorization": "bearer " + access_token})
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    me_json = response.json()
    return me_json['name']

def runFlask(portNumber, booleanDebug):
	app.run(port=portNumber, debug=booleanDebug)

if __name__ == '__main__':
	_thread.start_new_thread(runFlask,(65010, False))
#	appWx = wx.PySimpleApp()
#	frm = MyHtmlFrame(None, "Simple HTML Browser")
#	frm.Show()
	appWx2 = wx.App()
#	dialog = MyBrowser(None, -1)
	dialog = WebFrame(None,"ciao")
#	dialog.browser.LoadURL("http://localhost:65010")
	dialog.Show() 
	appWx2.MainLoop()
#	appWx.MainLoop()