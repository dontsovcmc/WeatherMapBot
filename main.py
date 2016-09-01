# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
import os

from report import report
from init import init
from bot import updater

def main(hook=False):
    init()

    if not hook:
        updater.start_polling()
        updater.idle()

    else:
        WEBHOOK_HOST = sys.argv[3]
        WEBHOOK_PORT = 443  # 443, 80, 88 или 8443
        WEBHOOK_LISTEN = '0.0.0.0'

        WEBHOOK_SSL_CERT = './webhook_cert.pem'
        WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

        WEBHOOK_URL = "https://%s:%d/%s" % (WEBHOOK_HOST, WEBHOOK_PORT, sys.argv[1])

        updater.start_webhook(listen=WEBHOOK_LISTEN, port=WEBHOOK_PORT,
            url_path=sys.argv[1],
            cert=WEBHOOK_SSL_CERT, key=WEBHOOK_SSL_PRIV,
            webhook_url='%s' % WEBHOOK_URL)

        updater.idle()


if __name__ == "__main__":

    if 'TRACK_ID' in os.environ:
        report.TRACK_ID = os.environ('TRACK_ID')
    else:
        if len(sys.argv) > 2:
            report.TRACK_ID = sys.argv[2]

    hook = len(sys.argv) > 3
    main(hook)
