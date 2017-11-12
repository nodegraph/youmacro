from time import sleep
from kivy.lib import osc

from service.ydlwrap import YdlWrap
from service.androidwrap import AndroidWrap

service_port = 7186


def extract_and_download(message, *args):
    print("got a message! %s" % message)

    try:
        # The current page url.
        page_url = message[2]

        # Extract the download url.
        url, filename = YdlWrap.extract_url(page_url)
        if url == '':
            return
        print('download_url: ' + url)

        # Create a name for the downloaded file.
        path = AndroidWrap.get_download_dir() + filename

        # Start the download.
        AndroidWrap.download_from_service(url, path)
    except Exception as e:
        print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEee error occurred during extract and download")
        print("Exception: %s" % e)

if __name__ == '__main__':
    print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB starting up')
    osc.init()
    oscid = osc.listen(ipAddr='127.0.0.1', port=service_port)
    osc.bind(oscid, extract_and_download, '/extract_and_download')

    while True:
        osc.readQueue(oscid)
        print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBbb background service')
        sleep(.1)
