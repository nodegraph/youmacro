from kivy.utils import platform
from jnius import autoclass
import os

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
    def get_activity_or_service():
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        if not (activity is None):
            return activity
        else:
            service = autoclass('org.kivy.android.PythonService').mService
            return service


    @staticmethod
    def download_from_service(url, filename):
        if platform == 'android':
            Environment = autoclass('android.os.Environment')
            Context = autoclass('android.content.Context')
            Request = autoclass('android.app.DownloadManager$Request')
            Uri = autoclass('android.net.Uri')

            # Create a request.
            uri = Uri.parse(url)
            request = Request(uri)
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
            request.setNotificationVisibility(Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            request.allowScanningByMediaScanner()

            # Send the request.
            caller = AndroidWrap.get_activity_or_service()
            download_manager = caller.getSystemService(Context.DOWNLOAD_SERVICE)
            download_manager.enqueue(request)

    @staticmethod
    def view_downloads():
        if platform == 'android':
            DownloadManager = autoclass('android.app.DownloadManager')
            Intent = autoclass('android.content.Intent')

            intent = Intent(DownloadManager.ACTION_VIEW_DOWNLOADS)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

            caller = AndroidWrap.get_activity_or_service()
            caller.startActivity(intent)