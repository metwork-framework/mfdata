#!/usr/bin/env python3

import ftplib
import datetime
import time
from mfutil import get_unique_hexa_identifier
from acquisition.step import AcquisitionStep


class FtpSendStep(AcquisitionStep):

    def init(self):
        self._session = None
        self._session_dt = None
        self._logger = self._get_logger()
        self.ftp_hostname = self.get_custom_config_value("ftp_hostname",
                                                         default="FIXME")
        self.ftp_username = self.get_custom_config_value("ftp_username",
                                                         default="FIXME")
        self.ftp_password = self.get_custom_config_value("ftp_password",
                                                         default="FIXME")
        if self.ftp_hostname == "FIXME" or self.ftp_hostname == "null" \
                or self.ftp_hostname == "":
            raise Exception("you have to set a valid ftp_hostname value")
        if self.ftp_username == "FIXME" or self.ftp_username == "null" \
                or self.ftp_username == "":
            raise Exception("you have to set a valid ftp_username value")
        if self.ftp_password == "FIXME" or self.ftp_password == "null" \
                or self.ftp_password == "":
            raise Exception("you have to set a valid ftp_password value")
        self.ftp_directory = self.get_custom_config_value("ftp_directory",
                                                          default=".")
        self.ftp_basename = self.get_custom_config_value(
            "ftp_basename", default="{ORIGINAL_BASENAME}")
        self.ftp_timeout = self.get_custom_config_value(
            "ftp_timeout", default=60, transform=int)
        self.ftp_connect_timeout = self.get_custom_config_value(
            "ftp_connect_timeout", default=30, transform=int)
        self.ftp_session_lifetime = self.get_custom_config_value(
            "ftp_session_lifetime", default=10, transform=int)
        self.tmp_suffix = self.get_custom_config_value(
            "tmp_suffix", default=".t")
        self._logger = self._logger.bind(hostname=self.ftp_hostname,
                                         user=self.ftp_username)

    def _get_session(self):
        if self._session is None:
            try:
                self._logger.debug("connecting...")
                self._session = \
                    ftplib.FTP(host=self.ftp_hostname, user=self.ftp_username,
                               passwd=self.ftp_password,
                               timeout=self.ftp_connect_timeout)
            except Exception as e:
                self._logger.warning("Exception: %s during FTP connect", e)
                self._session_dt = None
                return None
            if self.ftp_directory != '.':
                try:
                    self._logger.debug("changing directory to %s...",
                                       self.ftp_directory)
                    self._session.cwd(self.ftp_directory)
                except Exception as e:
                    self._logger.warning("Exception: %s during CWD on %s", e,
                                         self.ftp_directory)
                    self._session_dt = None
                    return None
        self._session_dt = datetime.datetime.now()
        return self._session

    def get_stor_name(self, xaf):
        step_counter = self._get_counter_tag_value(xaf, not_found_value='999')
        replaces = {
            "{RANDOM_ID}": get_unique_hexa_identifier(),
            "{ORIGINAL_BASENAME}": self.get_original_basename(xaf),
            "{ORIGINAL_DIRNAME}": self.get_original_dirname(xaf),
            "{ORIGINAL_UID}": self.get_original_uid(xaf),
            "{STEP_COUNTER}": str(step_counter)
        }
        stor_name = self.ftp_basename
        for to_replace, replaced in replaces.items():
            stor_name = stor_name.replace(to_replace, replaced)
        return time.strftime(stor_name)

    def process(self, xaf):
        session = self._get_session()
        if session is None:
            return False
        stor_name = self.get_stor_name(xaf)
        tmp_stor = stor_name + self.tmp_suffix
        try:
            with open(xaf.filepath, "rb") as f:
                session.storbinary("STOR %s" % tmp_stor, f)
        except Exception as e:
            self._logger.warning("Exception: %s during STOR %s" %
                                 (e, tmp_stor))
            return False
        try:
            if self.tmp_suffix != "":
                session.rename(tmp_stor, stor_name)
        except Exception as e:
            self._logger.warning("Exception: %s during RENAME %s %s" %
                                 (e, tmp_stor, stor_name))
            return False
        self.info("%s successfully uploaded to %s:%s/%s" %
                  (xaf.filepath, self.ftp_hostname,
                   self.ftp_directory, stor_name))
        return True

    def _close(self):
        try:
            self._session.quit()
        except Exception as e:
            self._logger.debug("can't quit ftp connection: %s", e)
        self._session = None
        self._session_dt = None

    def destroy(self):
        self._logger.info("closing ftp session")
        self._close()

    def ping(self):
        # called every second
        if self._session is not None and self._session_dt is not None:
            d = (datetime.datetime.now() - self._session_dt).total_seconds()
            if d > self.ftp_session_lifetime:
                self._logger.info("closing too old ftp session")
                self._close()


if __name__ == "__main__":
    x = FtpSendStep()
    x.run()
