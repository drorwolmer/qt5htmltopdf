import base64
import logging
import sys
import time
import argparse

from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtCore import QByteArray
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from xvfbwrapper import Xvfb

SLEEPING_TIME = 0.3
JS_CMD_TO_EVALUATE = "window.status"


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, cookie, parent=None):
        super().__init__(parent)
        self._cookie = cookie

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        info.setHttpHeader(b'Cookie', self._cookie)


def stop_and_exit(*args, exit_code=0, **kwargs):
    global q_app, vdisplay

    logging.info("Quitting")
    q_app.quit()
    vdisplay.stop()
    sys.exit(exit_code)


def check_window_status(window_status):
    global cmdline_args, start_time, q_page

    if window_status == cmdline_args.window_status:
        q_page.printToPdf(on_print_to_pdf)
    else:

        if (time.time() - start_time) > cmdline_args.timeout:
            logging.error("Timeout reached without '%s' equaling '%s'", JS_CMD_TO_EVALUATE, cmdline_args.window_status)
            stop_and_exit(exit_code=1)
            return

        time.sleep(SLEEPING_TIME)
        q_page.runJavaScript(JS_CMD_TO_EVALUATE, check_window_status)


def on_load_finished(load_ok):
    global cmdline_args ,q_page

    if not load_ok:
        logging.fatal("Failed _on_load_finished")
        stop_and_exit(exit_code=1)

    if cmdline_args.js_delay:
        logging.debug("Sleeping... %s seconds", cmdline_args.js_delay)
        time.sleep(cmdline_args.js_delay)

    if cmdline_args.window_status:
        q_page.runJavaScript(JS_CMD_TO_EVALUATE, check_window_status)
    else:
        q_page.printToPdf(on_print_to_pdf)


def on_print_to_pdf(data: QByteArray):
    global cmdline_args
    with open(cmdline_args.OUTPUT, "wb") as h:
        h.write(data.data())
    q_app.quit()


def parse_args():
    parser = argparse.ArgumentParser(description='Generate PDF from web pages using QT5')
    parser.add_argument("URL")
    parser.add_argument("OUTPUT", help="Output pdf file, or '-' for stdout")
    parser.add_argument('--timeout', help='Quit after this number of seconds', required=False, type=int)
    parser.add_argument('--window-status', help="Print only when '%s' matches this value" % JS_CMD_TO_EVALUATE,
                        required=False)
    parser.add_argument('--cookie', help='Use this cookie (must be Base64 encoded)', required=False)
    parser.add_argument('--js-delay', help='Wait this number of seconds before printing', required=False, type=int)
    args = parser.parse_args()

    if args.OUTPUT == "-":
        args.OUTPUT = "/dev/stdout"

    if args.cookie:
        try:
            args.cookie = base64.b64decode(cmdline_args.cookie)
        except:
            logging.exception("[-] Error decoding cookie!")
            sys.exit(1)

    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    cmdline_args = parse_args()

    vdisplay = Xvfb(width=1024, height=768, colordepth=24)
    vdisplay.start()

    q_app = QtWidgets.QApplication(sys.argv)
    q_view = QtWebEngineWidgets.QWebEngineView()
    q_page = q_view.page()

    if cmdline_args.cookie:
        req_interceptor = WebEngineUrlRequestInterceptor(cmdline_args.cookie)
        q_page.profile().setRequestInterceptor(req_interceptor)

    q_page.pdfPrintingFinished.connect(stop_and_exit)
    q_view.load(QtCore.QUrl(cmdline_args.URL))
    q_view.loadFinished.connect(on_load_finished)

    start_time = time.time()
    q_app.exec()
    vdisplay.stop()
