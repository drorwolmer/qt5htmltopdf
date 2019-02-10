import base64
import logging
import sys
import time
import argparse
from time import sleep

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtCore import QByteArray
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from xvfbwrapper import Xvfb

SLEEPING_TIME = 0.3


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, cookie, parent=None):
        super().__init__(parent)
        self.cookie = cookie

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        info.setHttpHeader(b'Cookie', self.cookie)


def _on_printing_finished(*args, **kwargs):
    logging.error("Quitting")
    q_app.quit()
    vdisplay.stop()
    sys.exit(1)


def _check_window_status(window_status):
    global cmdline_args, start_time

    if window_status == cmdline_args.window_status:
        q_page.printToPdf(_on_print_to_pdf)
    else:

        if (time.time() - start_time) > cmdline_args.timeout:
            logging.error("Timeout reached without window.status equaling '%s'", cmdline_args.window_status)
            _on_printing_finished()
            return

        time.sleep(SLEEPING_TIME)
        q_page.runJavaScript("window.status", _check_window_status)


def _on_load_finished(ok):
    global cmdline_args

    if not ok:
        logging.fatal("Failed _on_load_finished")
        _on_printing_finished()

    if cmdline_args.js_delay:
        logging.debug("Sleeping... %s seconds", cmdline_args.js_delay)
        sleep(cmdline_args.js_delay)

    if cmdline_args.window_status:
        # Start waiting for window.status
        q_page.runJavaScript("window.status", _check_window_status)
    else:
        q_page.printToPdf(_on_print_to_pdf)


def _on_print_to_pdf(data: QByteArray):
    global cmdline_args
    pdf_data = data.data()
    if cmdline_args.OUTPUT == "-":
        sys.stdout.buffer.write(pdf_data)
    else:
        with open(cmdline_args.OUTPUT, "wb") as h:
            h.write(pdf_data)
    q_app.quit()


def parse_args():
    parser = argparse.ArgumentParser(description='Create PDF from web')
    parser.add_argument("URL")
    parser.add_argument("OUTPUT", help="Output pdf file, or '-' for stdout")
    parser.add_argument('--timeout', help='Description for foo argument', required=False, type=int)
    parser.add_argument('--window-status', help="Print only when 'window.status' matches this value", required=False)
    parser.add_argument('--cookie', help='Use this cookie (must be Base64)', required=False)
    parser.add_argument('--js-delay', help='Wait this number of seconds before printing', required=False, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    cmdline_args = parse_args()

    vdisplay = Xvfb(width=1024, height=768, colordepth=24)
    vdisplay.start()

    q_app = QtWidgets.QApplication(sys.argv)
    q_view = QtWebEngineWidgets.QWebEngineView()
    q_page = q_view.page()

    if cmdline_args.cookie:
        try:
            cookie = base64.b64decode(cmdline_args.cookie)
        except:
            logging.error("[-] Error decoding cookie!")
            sys.exit(1)

        req_interceptor = WebEngineUrlRequestInterceptor(cookie)
        q_page.profile().setRequestInterceptor(req_interceptor)

    q_page.pdfPrintingFinished.connect(_on_printing_finished)
    q_view.load(QtCore.QUrl(cmdline_args.URL))
    q_view.loadFinished.connect(_on_load_finished)

    start_time = time.time()
    q_app.exec()
    vdisplay.stop()
