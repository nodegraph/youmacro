import youtube_dl

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
            'max_downloads': 1,
            'getfilename': True,
            'getthumbnail': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'restrictfilenames': True
        }

    @staticmethod
    def get_filename(info_dict):
        with youtube_dl.YoutubeDL(YdlWrap.get_default_opts('')) as ydl:
            return ydl.prepare_filename(info_dict)

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
        """Returns a tuple with the download url and the recommended filename to use.
        Note that the recommend filename will begin with a forward slash."""
        with youtube_dl.YoutubeDL(YdlWrap.get_default_opts("")) as ydl:
            print('111111111111111111')
            info_dict = ydl.extract_info(page_url, download=False, process=True)
            print('EEEEEE: ' + str(info_dict))

            # Determine a descriptive filename, deterministically.
            filename = YdlWrap.get_filename(info_dict)
            print('FFFFFFFFFFF filename is: %s' % filename)
            if filename == '/NA-NA.NA':
                return ('','')

            # If we get here, we have the download url and the recommended filename to use.
            if 'url' in info_dict:
                print('UUUUUUUUUUU url is: %s' % info_dict['url'])
                return (info_dict['url'], filename)

            # If we get here, we failed to find the download url.
            return ('','')