from __future__ import unicode_literals
import youtube_dl

import kivy

kivy.require('1.10.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from kivy.clock import Clock, mainthread
from android.runnable import run_on_ui_thread

from jnius import autoclass

import os

from pythonwebview.webviewwrapper import WebViewWrapper

# .webviewwrapper import WebViewWrapper

WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
activity = autoclass('org.kivy.android.PythonActivity').mActivity


# class WebViewWrap(Widget):
#    def __init__(self, **kwargs):                                                               
#        super(WebViewWrap, self).__init__(**kwargs)                                                      
#        Clock.schedule_once(self.create_webview, 0)                                             
#                                                                                                
#    @run_on_ui_thread                                                                           
#    def create_webview(self, *args):                                                            
#        webview = WebView(activity)                                                             
#        webview.getSettings().setJavaScriptEnabled(True)                                        
#        wvc = WebViewClient();                                                                  
#        webview.setWebViewClient(wvc);                                                          
#        activity.setContentView(webview)                                                        
#        webview.loadUrl('https://www.youtube.com')
#
# class Wv(Widget):
#    def __init__(self, **kwargs):
#        super(Wv, self).__init__(**kwargs)
#        Clock.schedule_once(self.create_webview, 0)
#
#    @run_on_ui_thread
#    def create_webview(self, *args):
#        webview = WebView(activity)
#        settings = webview.getSettings()
#        settings.setJavaScriptEnabled(True)
#        settings.setUseWideViewPort(True) # enables viewport html meta tags
#        settings.setLoadWithOverviewMode(True) # uses viewport
#
#        settings.setSupportZoom(True) # enables zoom
#        settings.setBuiltInZoomControls(True) # enables zoom controls
#        settings.setDisplayZoomControls(False)
#
#        settings.setScrollBarStyle(WebView.SCROLLBARS_OUTSIDE_OVERLAY)
#        settings.setScrollbarFadingEnabled(False)
#
#        #settings.setUserAgentString("\"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31");
#  #webview.setDesktopMode(True)
#
#
#        wvc = WebViewClient()
#        webview.setWebViewClient(wvc)
#        activity.setContentView(webview)
#        webview.loadUrl('https://www.youtube.com')

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class YdlWrap(object):
    @staticmethod
    def get_default_opts(download_dir):
        return {
            'outtmpl': download_dir + '/%(title)s-%(id)s.%(ext)s',
            'format': 'best',
            'logger': MyLogger(),
            'progress_hooks': [YdlWrap.on_progress],
        }

    @staticmethod
    def on_progress(info):
        if info['status'] == 'finished':
            print('Done downloading, now converting ...')
            print('on_progress: self: <%s> obj: <%s>' % (self, str(info)))

    @staticmethod
    def download(urls, download_dir):
        with youtube_dl.YoutubeDL(YdlWrap.get_default_opts(download_dir)) as ydl:
            ydl.download(urls)

    @staticmethod
    def extract_url(page_url):
        with youtube_dl.YoutubeDL(YdlWrap.get_default_opts("")) as ydl:
            info = ydl.extract_info(page_url, download=False)
            print('EEEEEE: ' + str(info))
            return info['url']


class AndroidWrap(object):
    @staticmethod
    def get_download_dir():
        if platform == 'android':
            Environment = autoclass('android.os.Environment')
            if Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED:
                return Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
        root = os.path.join(os.sep, os.getcwd(), 'Download')

    @staticmethod
    def get_download_dir_old():
        if platform == 'android':
            dir = os.getenv('EXTERNAL_STORAGE') or os.path.expanduser('~')
            dir = os.path.join(os.sep, dir, 'Download')
            # dir = os.path.join(os.sep, dir, 'youmacro')
            if not os.path.exists(dir):
                os.makedirs(dir)
            return dir
        return 'XXXX'

    @staticmethod
    def download(url, filename):
        if platform == 'android':
            Environment = autoclass('android.os.Environment')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            Sensor = autoclass('android.hardware.Sensor')
            DownloadManager = autoclass('android.app.DownloadManager')
            Request = autoclass('android.app.DownloadManager$Request')
            Uri = autoclass('android.net.Uri')

            # Get our activity.
            activity = PythonActivity.mActivity

            # Create a request.
            uri = Uri.parse(url)
            request = Request(uri)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
            request.setNotificationVisibility(Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.allowScanningByMediaScanner()

            # Send the request.
            download_manager = activity.getSystemService(Context.DOWNLOAD_SERVICE)
            download_manager.enqueue(request)


class YouMacroApp(App):
    def __init__(self, **kwargs):
        super(YouMacroApp, self).__init__(**kwargs)
        self.download_dir = AndroidWrap.get_download_dir()
        Clock.schedule_once(self._on_init_complete)

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def build(self):
        # self.icon = 'winter_hat_512.png'
        pass

    def _on_init_complete(self, *args):
        # Window.clearcolor = (0.1, 1, 0.1, 1)

        # Initialize our non-gui state.
        self.can_go_back = False
        self.can_go_forward = False

        # Grab our layouts.
        self.navbar_layout = self.root.ids.navbar_layout

        # Grab our navbar elements.
        self.address_bar = self.root.ids.address_bar
        self.address_bar.bind(on_text_validate=self.request_url)

        # Grab our toolbar buttons.
        self.download_button = self.root.ids.download_button
        self.download_button.bind(on_press=self.on_download)

        # Grab our web view placeholder where we inject the real web view.
        self.web_view_placeholder = self.root.ids.web_view_placeholder

        # Create the webview.
        self.wv_wrap = WebViewWrapper(self.navbar_layout)

        # Inject our webview into the placeholder.
        self.web_view_placeholder.add_widget(self.wv_wrap)

        # Hook up webview bindings.
        self.wv_wrap.bind(on_page_started=self.on_page_started)
        self.wv_wrap.bind(on_page_finished=self.on_page_finished)
        self.wv_wrap.bind(on_should_override_url_loading=self.on_should_override_url_loading)
        # self.web_view.bind(on_page_commit_visible=self.on_page_commit_visible)


    def request_url(self, pressed_obj):
        self._request_url(pressed_obj.text)

    @run_on_ui_thread
    def _request_url(self, url):
        self.wv_wrap.loadUrl(url)

    @run_on_ui_thread
    def update_url(self):
        url = self.wv_wrap.getUrl()
        self._update_url(url)

    @mainthread
    def _update_url(self, url):
        self._url = url
        self.set_address_bar(url)

    def set_address_bar(self, url):
        self.address_bar.text = url

    def on_download(self, pressed_obj):
        Clock.schedule_once(lambda elapsed_time: self._download(), 0)

    @run_on_ui_thread
    def _download(self):
        page_url = self.wv_wrap.getUrl()

        # Extract the download url.
        url = YdlWrap.extract_url(page_url)
        print('download_url: ' + url)

        # Create a name for the downloaded file.
        filename = os.path.join(os.sep, self.download_dir, 'test.mp4')

        # Start the download.
        AndroidWrap.download(url, filename)

    @run_on_ui_thread
    def go_back(self):
        """Go back a page."""
        if self.wv_wrap.canGoBack():
            self.wv_wrap.goBack()

    @run_on_ui_thread
    def go_forward(self):
        """Go forward a page."""
        if self.wv_wrap.canGoForward:
            self.wv_wrap.goForward()

    def on_should_override_url_loading(self, *args, **kwargs):
        """Handle on should override url loading events."""
        self.update_url()

    def on_page_started(self, *args, **kwargs):
        """Handle on page started events."""
        url = kwargs.get('url')
        if url is not None:
            self.set_address_bar(url)

    def on_page_finished(self, *args, **kwargs):
        """Handle on page finished events."""
        self.update_url()

    def on_page_commit_visible(self, *args, **kwargs):
        """Handle on page commit visible events."""
        self.update_url()


if __name__ == '__main__':
    YouMacroApp().run()
