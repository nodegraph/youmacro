import youtube_dl
from kivy.logger import Logger
from service.config import Config

class CachingLogger(object):
    """A basic logger for listening to log output from the caching process."""
    def debug(self, msg):
        if Config.Debug:
            Logger.info("Logger: %s" % str(msg))

    def warning(self, msg):
        if Config.Debug:
            Logger.warning("Logger: %s" % str(msg))

    def error(self, msg):
        if Config.Debug:
            Logger.error("Logger: %s" % str(msg))

class CachingProgressListener(object):
    """A basic listener which listens to progress from the caching progress."""
    def on_progress(self, info):
        print('on_progress: self: <%s> obj: <%s>' % (self, str(info)))
        return
        if info['status'] == 'finished':
            print('Done downloading, now converting ...')
            print('on_progress: self: <%s> obj: <%s>' % (self, str(info)))

class Cacher(object):
    """This """
    def __init__(self, download_dir, progress_listeners, logger = CachingLogger()):
        # Create ouR options.
        self._opts = {
            'outtmpl': download_dir + '/%(title)s-%(id)s.%(ext)s',
            'format': 'best',
            'logger': logger,
            'progress_hooks': progress_listeners,
            'max_downloads': 1,
            'getfilename': True,
            'getthumbnail': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'restrictfilenames': True
        }

    def cache_media(self, page_urls):
        return youtube_dl.YoutubeDL(self._opts).download(page_urls)

    def get_media_filename(self, info_dict):
        return youtube_dl.YoutubeDL(self._opts).prepare_filename(info_dict)

    def get_media_url(self, page_url):
        """Returns a tuple with the download url and the recommended filename to use.
        Note that the recommend filename will begin with a forward slash."""
        info_dict = youtube_dl.YoutubeDL(self._opts).extract_info(page_url, download=False, process=True)

        # Determine a descriptive filename, deterministically.
        filename = Cacher.get_media_filename(info_dict)
        print('FFFFFFFFFFF filename is: %s' % filename)
        if filename == '/NA-NA.NA':
            return ('','')

        # If we get here, we have the download url and the recommended filename to use.
        if 'url' in info_dict:
            print('UUUUUUUUUUU url is: %s' % info_dict['url'])
            return (info_dict['url'], filename)

        # If we get here, we failed to find the download url.
        return ('','')