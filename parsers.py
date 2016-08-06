
__author__ = 'Dontsov Evgeny'

import bs4
from network import Downloader
from maps import eparsetype
from datetime import datetime


def current_map_urls(sql_map):
    """
    :return: [(timestamp UTC, url)]
    """
    frames = []
    if sql_map.parse_type_id == eparsetype.GISMETEO_MAP:

        with Downloader() as d:
            data = d.getresponse(sql_map.url)
            soup = bs4.BeautifulSoup(data, "html.parser")

        tab_i = 0
        try:
            while True:
                imgs = soup.select('.tab%s > img' % tab_i)
                if not len(imgs):
                    break
                for i in imgs:
                    date_object = datetime.strptime(i.attrs['alt'], '%d.%m.%Y %H:%M')
                    OFFSET = datetime.utcnow() - datetime.now()
                    date_object = date_object + OFFSET
                    frame = date_object, 'https:' + i.attrs['title']
                    frames.append(frame)
                tab_i += 1
        except Exception, err:
            pass

    elif sql_map.parse_type_id == eparsetype.PICTURE_MAP:

        frames.append((datetime.utcnow(), sql_map.url))

    return frames
