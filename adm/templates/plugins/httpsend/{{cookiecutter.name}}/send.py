#!/usr/bin/env python3

import time
import requests
from mfutil import get_unique_hexa_identifier
from acquisition import AcquisitionStep


class Step{{cookiecutter.name|capitalize}}Send(AcquisitionStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "send"
    _session = None
    _ok_status_codes = None

    def _get_session(self):
        if self._session is None:
            self._session = requests.session()
        return self._session

    def _get_url(self, xaf):
        step_counter = self._get_counter_tag_value(xaf, not_found_value='999')
        replaces = {
            "{RANDOM_ID}": get_unique_hexa_identifier(),
            "{ORIGINAL_BASENAME}": self.get_original_basename(xaf),
            "{ORIGINAL_DIRNAME}": self.get_original_dirname(xaf),
            "{ORIGINAL_UID}": self.get_original_uid(xaf),
            "{STEP_COUNTER}": str(step_counter)
        }
        url = self.args.http_url
        for to_replace, replaced in replaces.items():
            url = url.replace(to_replace, replaced)
        return time.strftime(url)

    def add_extra_arguments(self, parser):
        parser.add_argument('--http-method', type=str, default='PUT',
                            help='http method')
        parser.add_argument('--http-url', type=str,
                            help='http url to invoke with the file as body')
        parser.add_argument('--http-timeout', type=int, default=60,
                            help='http timeout (in seconds)')
        parser.add_argument('--http-ok-status-codes', type=str,
                            default="200,201",
                            help='coma seperated list of "ok" status codes')

    def init(self):
        if self.args.http_url is None:
            raise Exception("http-url option can't be empty")
        if self.args.http_method not in ['PUT', 'POST', 'GET', 'OPTIONS',
                                         'HEAD', 'PATCH', 'DELETE']:
            raise Exception("http-method must be PUT, POST, GET, OPTIONS, "
                            "HEAD, PATCH or DELETE")
        self._ok_status_codes = \
            [int(x) for x in self.args.http_ok_status_codes.split(',')]

    def process(self, xaf):
        session = self._get_session()
        with open(xaf.filepath, 'rb') as f:
            url = self._get_url(xaf)
            self.info("invoking %s on %s" % (self.args.http_method, url))
            reply = session.request(self.args.http_method, url,
                                    timeout=self.args.http_timeout, data=f)
            self.debug("status_code=%i" % reply.status_code)
            if reply.status_code in self._ok_status_codes:
                return True
            else:
                self.warning("not ok status_code=%i during %s on %s" %
                             (reply.status_code, self.args.http_method, url))
        return False


if __name__ == "__main__":
    x = Step{{cookiecutter.name|capitalize}}Send()
    x.run()
