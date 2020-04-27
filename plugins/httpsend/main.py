#!/usr/bin/env python3

import time
import requests
from mfutil import get_unique_hexa_identifier
from acquisition import AcquisitionStep


class HttpSendStep(AcquisitionStep):

    def init(self):
        self.http_method = self.get_custom_config_value("http_method",
                                                        default="PUT").upper()
        if self.http_method not in ['PUT', 'POST', 'GET', 'OPTIONS',
                                    'HEAD', 'PATCH', 'DELETE']:
            raise Exception("http-method: %s must be PUT, POST, GET, OPTIONS, "
                            "HEAD, PATCH or DELETE" % self.http_method)
        self.http_url = self.get_custom_config_value("http_url",
                                                     default=None)
        if self.http_url is None:
            raise Exception("you have to set an http_url configuration value")
        self.http_timeout = self.get_custom_config_value("http_timeout",
                                                         default=60,
                                                         transform=int)
        self.http_ok_status_codes = \
            [int(x) for x in self.get_custom_config_value(
                "http_ok_status_codes", default="200,201").split(',')]
        self._session = None

    def _get_session(self):
        if self._session is None:
            self._session = requests.session()
        return self._session

    def get_url(self, xaf):
        step_counter = self._get_counter_tag_value(xaf, not_found_value='999')
        replaces = {
            "{RANDOM_ID}": get_unique_hexa_identifier(),
            "{ORIGINAL_BASENAME}": self.get_original_basename(xaf),
            "{ORIGINAL_DIRNAME}": self.get_original_dirname(xaf),
            "{ORIGINAL_UID}": self.get_original_uid(xaf),
            "{STEP_COUNTER}": str(step_counter)
        }
        url = self.http_url
        for to_replace, replaced in replaces.items():
            url = url.replace(to_replace, replaced)
        return time.strftime(url)

    def process(self, xaf):
        session = self._get_session()
        with open(xaf.filepath, 'rb') as f:
            url = self.get_url(xaf)
            self.info("invoking %s on %s ..." % (self.http_method, url))
            reply = session.request(self.http_method, url,
                                    timeout=self.http_timeout, data=f)
            if reply.status_code in self.http_ok_status_codes:
                self.info("ok (status_code=%i)" % reply.status_code)
                return True
            else:
                self.warning("not ok (status_code=%i during %s on %s)" %
                             (reply.status_code, self.http_method, url))
        return False


if __name__ == "__main__":
    x = HttpSendStep()
    x.run()
