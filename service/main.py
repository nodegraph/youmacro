from time import sleep
from kivy.lib import osc
from kivy.logger import Logger

from service.cacher import Cacher
from service.androidwrap import AndroidWrap
from service.comms import Comms

from jnius import autoclass
from jnius import cast

import os
import copy

# Activity related classes.
JPythonActivity = autoclass('org.kivy.android.PythonActivity')

# Service related classes.
JCachingService = autoclass('{}.Service{}'.format('com.youmacro.browser', 'Downloader'))
JPythonService = autoclass('org.kivy.android.PythonService')
j_python_service = JPythonService.mService

# Intent related classes.
JContext = autoclass('android.content.Context')
JIntent = autoclass('android.content.Intent')
JPendingIntent = autoclass('android.app.PendingIntent')

# Notification classes.
JNotificationBuilder = autoclass('android.app.Notification$Builder')
JAction = autoclass('android.app.Notification$Action')

# Basic classes.
JFile = autoclass('java.io.File')
JString = autoclass('java.lang.String')
JArrayList = autoclass('java.util.ArrayList')
JUri = autoclass('android.net.Uri')
JBundle = autoclass('android.os.Bundle')

# Icon related classes.
JDimen = autoclass("android.R$dimen")
JBitmap = autoclass("android.graphics.Bitmap")
JDrawable = autoclass("{}.R$drawable".format(j_python_service.getPackageName()))



class CachingService(object):
    def __init__(self):
        self._cacher = Cacher(AndroidWrap.get_download_dir(), [self.on_progress])
        self._current_notification_id = 0
        self._current_pending_intent_id = 0
        self._large_icon = CachingService.get_scaled_icon('icon')

    def on_progress(self, info):
        print('on_progress: self: <%s> obj: <%s>' % (self, str(info)))
        status = info['status']

        # Form the title.
        filepath = info['filename']
        filename = os.path.basename(filepath)
        title = filename
        print('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFf file path: %s' % filepath)

        # Form the message.
        message = ''
        if status == 'downloading':
            percent_string = info['_percent_str']
            total_bytes_str = info['_total_bytes_str']
            speed_str = info['_speed_str']
            message = percent_string + ' of ' + total_bytes_str + ' at ' + speed_str
            self.post_progress(title, message)

        elif status == 'finished':
            elapsed_str = info['_elapsed_str']
            total_bytes_str = info['_total_bytes_str']
            message = 'downloaded ' + total_bytes_str + ' in ' + elapsed_str
            self.post_finished(title, message, filepath)


    def extract_and_download_old(self, message, *args):
        """This method first extracts the url for the video on the page. Then it downloads it using Android's download
        manager app. Note that this only works when the extracted url points to a single video file such as mp4. When
        the url points to streaming formats like dash, Android's download manager app will not be able to downloading
        this as the data comes in through multiple files which then need to be concatenated. So do not use this method.
        It is only kept for reference purposes."""
        try:
            # Get the current page's url.
            page_url = message[2]

            # Extract the download url.
            url, filename = self._cacher.get_media_url(page_url)
            if url == '':
               return
            print('download_url: ' + url)

            # Create a name for the downloaded file.
            path = AndroidWrap.get_download_dir() + filename

            # Start the download.
            AndroidWrap.download_from_service(url, path)

        except Exception as e:
            print("Exception: %s" % e)

    def extract_and_download(self, message, *args):
        self.post_starting()
        print ("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        print("message: %s" % message)
        """This method uses youtube_dl to download the video, given the webpage's url."""
        try:
            # Get the current page's url.
            page_url = message[2]
            self._cacher.cache_media([page_url])
        except Exception as e:
            print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEee error occurred during extract and download")
            print("Exception: %s" % e)

    def post_starting(self):
        intent = self.create_self_intent()
        self.post(u'Processing Web Page', u'Looking for links in the web page.', intent)

    def post_progress(self, title, message):
        intent = self.create_self_intent()
        self.post(title, message, intent)

    def post_finished(self, title, message, filepath):
        intent = self.create_playback_intent(filepath)
        self.post(title, message, intent)
        # Update our current notification id.
        self._current_notification_id += 1

    @staticmethod
    def create_self_intent():
        """Create an intent which launches our main activity."""
        context = j_python_service.getApplication().getApplicationContext()
        intent = JIntent(context, JPythonActivity)
        intent.setFlags(
            JIntent.FLAG_ACTIVITY_CLEAR_TOP | JIntent.FLAG_ACTIVITY_SINGLE_TOP | JIntent.FLAG_ACTIVITY_NEW_TASK)
        intent.setAction(JIntent.ACTION_MAIN)
        intent.addCategory(JIntent.CATEGORY_LAUNCHER)
        return intent

    @staticmethod
    def create_playback_intent(filepath):
        """Create an intent which uses the user's default app to play video."""
        # Convert some python str types into java strings.
        filepath = u'file://' + filepath
        filepath = JString(filepath.encode('utf-16'), 'utf-16')

        intent = JIntent(JIntent.ACTION_VIEW)
        mime_type = JString(u'video/*'.encode('utf-16'), 'utf-16')
        intent.setDataAndType(JUri.parse(filepath), mime_type)
        return intent

    def post(self, title, message, intent = None):
        # Convert some python str types into java strings.
        title = JString(title.encode('utf-16'), 'utf-16')
        message = JString(message.encode('utf-16'), 'utf-16')

        # Setup our notification builder.
        builder = JNotificationBuilder(j_python_service)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setSmallIcon(JDrawable.icon)
        builder.setLargeIcon(self._large_icon)

        if intent:
            # Wrap the intent into a pending intent.
            pending_intent = JPendingIntent.getActivity(j_python_service, self._current_pending_intent_id, intent, 0)

            # Increment the pending intent id counter.
            self._current_pending_intent_id += 1

            # Configure the builder to use the pending intent.
            builder.setContentIntent(pending_intent)

        # Build our notification.
        notification = builder.getNotification()

        # Use the notification service to post it.
        notification_service = j_python_service.getSystemService(JContext.NOTIFICATION_SERVICE)
        notification_service.notify(self._current_notification_id, notification)





    @staticmethod
    def get_scaled_icon(icon):
        """
        icon : name of icon file (png) without extension
        """
        scaled_icon = getattr(JDrawable, icon)
        scaled_icon = cast("android.graphics.drawable.BitmapDrawable",
                           j_python_service.getResources().getDrawable(scaled_icon))
        scaled_icon = scaled_icon.getBitmap()

        res = j_python_service.getResources()
        height = res.getDimension(JDimen.notification_large_icon_height)
        width = res.getDimension(JDimen.notification_large_icon_width)
        return JBitmap.createScaledBitmap(scaled_icon, width, height, False)

    @staticmethod
    def intent_callback(context, intent, *args):
        ''' Notification Button Callback
        If everything was working correctly, this function would be called
        when the user press a notification button.
        '''
        # context, intent
        Logger.warning("captured intent")
        Logger.warning("%s" % context)
        Logger.warning("%s" % intent)
        Logger.warning("%s" % args)


if __name__ == '__main__':
    caching_service = CachingService()

    osc.init()
    oscid = osc.listen(ipAddr='127.0.0.1', port=Comms.service_port)
    osc.bind(oscid, caching_service.extract_and_download, '/extract_and_download')

    while True:
        osc.readQueue(oscid)
        print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBbb background service')
        sleep(.1)
