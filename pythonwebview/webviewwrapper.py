"""This module contains our main WebView widget for Kivy."""

from kivy.core.window import Window

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.uix.actionbar import ActionView, ActionBar, ActionButton
from kivy.uix.widget import Widget

from android.runnable import run_on_ui_thread
from jnius import autoclass

from webviewclient import create_forwarding_web_view_client

# Reference android classes.
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
View = autoclass('android.view.View')
activity = autoclass('org.kivy.android.PythonActivity').mActivity


class WebViewWrapper(Widget, EventDispatcher):

    _events = ['on_should_override_url_loading', 'on_page_started', 'on_page_finished', 'on_received_error',
               'on_page_commit_visible', 'on_back_button']

    def __init__(self, action_bar):
        """The Web View Wrapper is a Kivy Widget, which creates and manages a native android web view.
        The methods from the native android web view are exposed on this class. The calls are passed
        to the native android view. The actual native web view is constructed later on the ui thread.
        """
        self.action_bar = action_bar
        self._web_view = None

        # Register the events we're interested in.
        self._register_events()

        # Call our parent constructors.
        super(WebViewWrapper, self).__init__()

        # Create our web view on the ui thread.
        self.create_web_view()

    def dispatch_event(self, event_name, **kwargs):
        print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE Event %s dispatched \n' % event_name, kwargs)
        self.dispatch(event_name, **kwargs)

    def _event_default_handler(self, **kwargs):
        pass

    def _register_events(self):
        events = self._events
        for event_name in events:
            setattr(self, event_name, self._event_default_handler)
            self.register_event_type(event_name)

    def __getattr__(self, method_name):
        """Expose the native web view methods on this class."""
        if hasattr(self._web_view, method_name):
            return lambda *x: getattr(self._web_view, method_name)(*x)
        else:
            raise Exception("WebViewWrapper::%s was not defined." % method_name)

    def on_size(self, *args):
        """Called when the screen orientation changes."""
        # Layout the web view on the ui thread.
        self.layout_web_view()

    @run_on_ui_thread
    def layout_web_view(self):
        if not self._web_view:
            return

        print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        # Set the top left corner.
        self._web_view.setX(0)
        print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
        self._web_view.setY(Window.height * 0.08) #(self.action_bar.height)
        print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')


        # Set the layout params.
        lp = self._web_view.getLayoutParams()
        print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
        lp.height = Window.height * 0.92
        print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
        lp.width = Window.width
        print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

        # Request another layout run.
        self._web_view.requestLayout()
        print('GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG')

    @run_on_ui_thread
    def create_web_view(self):
        """Create the web view."""

        # Return if a web view has already been created.
        if self._web_view:
            return True

        # Create the native android web view.
        self._web_view = WebView(activity)

        # Setup the web view.
        settings = self._web_view.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setUseWideViewPort(True)  # enables viewport html meta tags
        settings.setLoadWithOverviewMode(True)  # uses viewport
        settings.setSupportZoom(True)  # enables zoom
        settings.setBuiltInZoomControls(True)  # enables zoom controls

        # Set the forwarding web view client.
        # This allows us to get events from the native web view.
        self.client = create_forwarding_web_view_client(self)
        self._web_view.setWebViewClient(self.client)

        # Set the top left corner.
        self._web_view.setX(0)
        self._web_view.setY(Window.height * 0.08)

        # Add the web view to our view.
        height = Window.height * 0.92
        width = Window.width
        activity.addContentView(self._web_view, LayoutParams(width, height))
        self._web_view.loadUrl('https://www.youtube.com')

    @run_on_ui_thread
    def destroy_web_view(self):
        if self._web_view:
            self._web_view.clearHistory()
            self._web_view.clearCache(True)
            self._web_view.loadUrl("about:blank")
            self._web_view = None

    @run_on_ui_thread
    def hide_web_view(self):
        """Hides the web view."""
        if self._web_view is None:
            return False
        self._web_view.setVisibility(View.GONE)

    @run_on_ui_thread
    def show_web_view(self):
        """Show the web view."""
        if self._web_view is None:
            return False
        self._web_view.setVisibility(View.VISIBLE)