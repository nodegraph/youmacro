import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.lib import osc
from kivy.uix.actionbar import ActionButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from android import activity
from android.runnable import run_on_ui_thread
from jnius import autoclass
from jnius import cast

# Our classes.
from pythonwebview.webviewwrapper import WebViewWrapper
from service.androidwrap import AndroidWrap
from service.comms import Comms
from service.config import Config as AppConfig

JIntent = autoclass('android.content.Intent')
JString = autoclass('java.lang.String')
JUri = autoclass('android.net.Uri')

# Ad Service Classes.
AdBuddiz=autoclass("com.purplebrain.adbuddiz.sdk.AdBuddiz")

# WebView Classes.
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
Intent = autoclass('android.content.Intent')

# Our android activity.
PythonActivity=autoclass("org.kivy.android.PythonActivity")
activity = PythonActivity.mActivity

# Our service
Service = autoclass('{}.Service{}'.format('com.youmacro.browser', 'Downloader'))
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
AndroidString = autoclass('java.lang.String')
NotificationBuilder = autoclass('android.app.Notification$Builder')


Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'pause_on_minimize', 0)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)


class SearchBar(TextInput, ActionButton):
    """This is an invisible tiny search bar.
    It's purpose is to make sure the ActionBar draws properly after orientation changes.
    Kivy seems to have a but where it doesn't without this."""
    def __init__(self, *args, **kwargs):
        super(SearchBar, self).__init__(*args, **kwargs)
        self.hint_text=''
        # self.background_color = [0, 0, 0, 1]


class YouMacroApp(App):
    def __init__(self, **kwargs):
        super(YouMacroApp, self).__init__(**kwargs)
        Clock.schedule_once(self._on_init_complete)

        import android.activity
        android.activity.bind(on_new_intent=self.on_new_intent)

    def on_start(self):
        # Bind some event handlers.
        EventLoop.window.bind(on_key_down=self.handle_key_down)

        # Add this to manifest for AdBuddiz.
        #<activity android:name = "com.purplebrain.adbuddiz.sdk.AdBuddizActivity"
        #    android:theme = "@android:style/Theme.Translucent" />

        # Start up ad service.
        # AdBuddiz has a rule about multiple installations on same device.
        # So put it in test mode when developing. This must come before setPublisherKey.
        if AppConfig.Debug:
            AdBuddiz.setTestModeActive()
            AdBuddiz.setPublisherKey("TEST_PUBLISHER_KEY")
        else:
            AdBuddiz.setPublisherKey("e5ad34cb-e1e1-4fca-8f98-cc412b5d0fa6")

        # Cache some ads.
        AdBuddiz.cacheAds(activity)
        return True

    def on_pause(self):
        # Note the pause logic partially kills the Kivy app.
        # So we procedurally press the home button to send the app to the background,
        # before we get here. We only get here when the native WebView has focus.
        # Otherwise we can catch the back button in the normal key down handler.
        # if platform == 'android':
        #     # move activity to back
        #     activity.moveTaskToBack(True)
        return True

    def on_resume(self):
        # These prints seem to make kivy refresh the ui properly when resuming,
        # aftering pressing the back button to close down the download manager.
        print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr')
        print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr')
        print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr')

    def some_api_callback(self, message, *args):
        print("got a message! %s" % message)

    @run_on_ui_thread
    def start_service(self):
        argument = ''
        Service.start(activity, argument)

    def build(self):
        # Start our background service.
        self.start_service()

        # Initialize osc for communicating with the background service.
        # Note we only do one way communication from the main app to the service.
        osc.init()
        #oscid = osc.listen(ipAddr='127.0.0.1', port=app_port)
        #print('OOOOOOOOOOOOOOOOOOOOOOOO oscid is: %s' % oscid)
        #osc.bind(oscid, self.some_api_callback, '/download_url_found')
        #Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)

        # Sometimes the service seems to get killed.
        # So we periodically (every 2 seconds) call start service to make sure the service is started.
        Clock.schedule_interval(lambda dt: self.start_service(), 2)



    def on_new_intent(self, intent):
        print('IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')

        # Check the intent for extra arguments.
        extras = intent.getExtras()
        if extras:
            extra_name = JString(u'com.youmacro.browser.filepath'.encode('utf-16'),'utf-16')
            #extra_jstr = extras.get(JIntent.EXTRA_STREAM)
            #extra_jstr = extra_jstr.decode('utf16')
            #uri = cast('android.net.Uri', extras.getParcelable(JIntent.EXTRA_STREAM))
            #extra_jstr = uri.toString()
            extra_jstr = extras.getShortArray(JIntent.EXTRA_STREAM)
            print('extra: %s' % extra_jstr)
            if extra_jstr:
                print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                intent = JIntent(JIntent.ACTION_VIEW)
                type = JString('video/*'.encode('utf8'))
                intent.setDataAndType(extra_jstr, type)
                activity.startActivity(intent)
        else:
            print('nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn no extras')

    def _on_init_complete(self, *args):
        # Window.clearcolor = (0.1, 1, 0.1, 1)

        # Initialize our non-gui state.
        self.can_go_back = False
        self.can_go_forward = False

        # Grab our action bar elements.
        self.action_bar = self.root.ids.action_bar

        # Grab our toolbar buttons.
        self.youmacro_button = self.root.ids.youmacro_button
        self.youmacro_button.bind(on_press=self.on_youmacro_pressed)

        self.search_button = self.root.ids.search_button
        self.search_button.bind(on_press=self.on_search_pressed)

        self.refresh_button = self.root.ids.refresh_button
        self.refresh_button.bind(on_press=self.on_refresh_pressed)

        self.back_button = self.root.ids.back_button
        self.back_button.bind(on_press=self.on_back_pressed)

        self.forward_button = self.root.ids.forward_button
        self.forward_button.bind(on_press=self.on_forward_pressed)

        self.download_button = self.root.ids.download_button
        self.download_button.bind(on_press=self.on_download_pressed)

        self.play_button = self.root.ids.play_button
        self.play_button.bind(on_press=self.on_play_pressed)

        # Grab our web view placeholder where we inject the real web view.
        self.web_view_placeholder = self.root.ids.web_view_placeholder

        # Create the webview.
        self.wv_wrap = WebViewWrapper(self.action_bar)

        # Inject our webview into the placeholder.
        self.web_view_placeholder.add_widget(self.wv_wrap)

        # Hook up webview bindings.
        self.wv_wrap.bind(on_page_started=self.on_page_started)
        self.wv_wrap.bind(on_page_finished=self.on_page_finished)
        self.wv_wrap.bind(on_should_override_url_loading=self.on_should_override_url_loading)
        self.wv_wrap.bind(on_back_button=self.on_back_button)

    # ---------------------------------------------------------------------------
    # Kivy Widget Event Handlers.
    # ---------------------------------------------------------------------------

    def on_youmacro_pressed(self, pressed_obj):
        self.perform_youmacro_action()

    def on_search_pressed(self, pressed_obj):
        self.perform_search_action()

    def on_refresh_pressed(self, pressed_obj):
        self.perform_refresh_action()

    def on_back_pressed(self, pressed_obj):
        self.perform_back_action()

    def on_forward_pressed(self, pressed_obj):
        self.perform_forward_action()

    def on_download_pressed(self, pressed_obj):
        # We currently on show ads on downloads.
        AdBuddiz.showAd(activity)
        self.perform_download_action()

    def on_play_pressed(self, pressed_obj):
        self.perform_play_action()

    @run_on_ui_thread
    def perform_youmacro_action(self):
        self.wv_wrap.loadUrl("http://youmacro.com/topvideos/index.html")

    @run_on_ui_thread
    def perform_search_action(self):
        self.wv_wrap.loadUrl("https://www.google.com")

    @run_on_ui_thread
    def perform_refresh_action(self):
        self.wv_wrap.reload()

    @run_on_ui_thread
    def perform_back_action(self):
        """Go back a page."""
        if self.wv_wrap.canGoBack():
            self.wv_wrap.goBack()

    @run_on_ui_thread
    def perform_forward_action(self):
        """Go forward a page."""
        if self.wv_wrap.canGoForward:
            self.wv_wrap.goForward()

    @run_on_ui_thread
    def perform_download_action(self):
        page_url = self.wv_wrap.getUrl()
        osc.sendMsg('/extract_and_download', [page_url], port=Comms.service_port)

    @staticmethod
    def debug_download_action(page_url):
        """This downloads on the main thread.
        It's purpose is to help debug YDL, as we get a good stack trace on the main thread."""
        #url = YdlWrap.get_media_url(page_url)
        print('dddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
        print('download_url: ' + url)
        print('dddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')

    @run_on_ui_thread
    def perform_play_action(self):
        AndroidWrap.view_downloads()



    # ---------------------------------------------------------------------------
    # WebViewClient Event Handlers.
    # ---------------------------------------------------------------------------

    def on_should_override_url_loading(self, *args, **kwargs):
        """Handle on should override url loading events."""
        pass

    def on_page_started(self, *args, **kwargs):
        """Handle on page started events."""
        pass

    def on_page_finished(self, *args, **kwargs):
        """Handle on page finished events."""
        pass

    def on_page_commit_visible(self, *args, **kwargs):
        """Handle on page commit visible events."""
        pass

    @run_on_ui_thread
    def on_back_button(self, *args, **kwargs):
        # Procedurally press the home button to put this activity in the background.
        # Otherwise Kivy's on_pause logic will partially kill the app,
        # making it unusable with a black screen when resumed.
        intent = Intent(Intent.ACTION_MAIN)
        intent.addCategory(Intent.CATEGORY_HOME)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(intent)

    # ---------------------------------------------------------------------------
    # EventLoop Event Handlers.
    # ---------------------------------------------------------------------------

    def handle_key_down(self, key, scancode, codepoint, modifier, other):
        # We can detect back button presses here on app start/resume when the webview
        # has not received focus yet. To avoid confusing the user we make sure to use
        # the same logic as when the back button is pressed and webview has had focus.
        if scancode == 27:
            self.on_back_button()
        return True


if __name__ == '__main__':
    YouMacroApp().run()
