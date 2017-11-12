"""This module holds logic to build a java based ForwardingWebViewClient.
"""

from jnius import autoclass
from jnius import PythonJavaClass
from jnius import java_method

ForwardingWebViewClient = autoclass('com.youmacro.javawebview.ForwardingWebViewClient')


def create_forwarding_web_view_client(python_listener):
    """Create a Forwarding Web View Client."""

    # Create our object which acts like a java/jni callable object.
    java_listener = JavaListener(python_listener)
    # Store a reference to this on the python listener as it seems to get garbage collected after downloads.
    python_listener.java_listener = java_listener
    # Finally create the java based ForwardingWebViewClient.
    return ForwardingWebViewClient(java_listener)


class JavaListener(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['com.youmacro.javawebview.WebViewEventsListenerInterface']

    def __init__(self, python_listener):
        """Instances of this act like java/jni callable objects."""
        super(JavaListener, self).__init__()
        self._python_listener = python_listener

    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
    def shouldOverrideUrlLoading(self, view, url):
        self._python_listener.dispatch_event('on_should_override_url_loading', webview=view, url=url)

    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;Landroid/graphics/Bitmap;)V')
    def onPageStarted(self, view, url, favicon):
        self._python_listener.dispatch_event('on_page_started', webview=view, url=url, favicon=favicon)

    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
    def onPageFinished(self, view, url):
        self._python_listener.dispatch_event('on_page_finished', webview=view, url=url)

    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
    def onPageCommitVisible(self, view, url):
        self._python_listener.dispatch_event('on_page_commit_visible', webview=view, url=url)

    @java_method('(Landroid/webkit/WebView;Ljava/lang/Integer;Ljava/lang/String;Ljava/lang/String;)V')
    def onReceivedError(self, view, errorCode, description, failingUrl):
        self._python_listener.dispatch_event('on_received_error', webview=view, error_code=errorCode,
                                             description=description, failing_url=failingUrl)

    @java_method('(Landroid/webkit/WebView;)V')
    def onBackButton(self, view):
        self._python_listener.dispatch_event('on_back_button', webview=view)