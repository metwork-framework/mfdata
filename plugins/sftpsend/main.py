#!/usr/bin/env python3

import paramiko
import datetime
import time
from mfutil import get_unique_hexa_identifier
from acquisition.step import AcquisitionStep


class SftpSendStep(AcquisitionStep):

    def init(self):
        self._session = None
        self._session_dt = None
        self._logger = self._get_logger()
        self.sftp_hostname = self.get_custom_config_value("sftp_hostname",
                                                          default="FIXME")
        self.sftp_username = self.get_custom_config_value("sftp_username",
                                                          default="FIXME")
        self.sftp_password = self.get_custom_config_value("sftp_password",
                                                          default="FIXME")
        if self.sftp_hostname == "FIXME" or self.sftp_hostname == "null" \
                or self.sftp_hostname == "":
            raise Exception("you have to set a valid sftp_hostname value")
        if self.sftp_username == "FIXME" or self.sftp_username == "null" \
                or self.sftp_username == "":
            raise Exception("you have to set a valid sftp_username value")
        self.sftp_key_file = self.get_custom_config_value("sftp_key_file")
        if self.sftp_password == "" and self.sftp_key_file == "":
            raise Exception("you have to set a valid authentication method"
                            " value (sftp_password or sftp_key_file)")
        self.sftp_key_file_passphrase = self.get_custom_config_value(
            "sftp_key_file_passphrase")
        self.sftp_key_disabled_algorithms = self.get_custom_config_value(
            "sftp_key_disabled_algorithms")
        self.sftp_directory = self.get_custom_config_value("sftp_directory",
                                                           default=".")
        self.sftp_basename = self.get_custom_config_value(
            "sftp_basename", default="{ORIGINAL_BASENAME}")
        self.sftp_timeout = self.get_custom_config_value(
            "sftp_timeout", default=60, transform=int)
        self.sftp_connect_timeout = self.get_custom_config_value(
            "sftp_connect_timeout", default=30, transform=int)
        self.sftp_session_lifetime = self.get_custom_config_value(
            "sftp_session_lifetime", default=10, transform=int)
        self.tmp_suffix = self.get_custom_config_value(
            "tmp_suffix", default=".t")
        self._logger = self._logger.bind(hostname=self.sftp_hostname,
                                         user=self.sftp_username)

    def _get_session(self):
        if self._session is None:
            try:
                self._logger.debug("connecting...")

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if self.sftp_key_file:
                    # connect with SSH private key file
                    if self.sftp_key_file_passphrase:
                        # with passphrase
                        key = paramiko.RSAKey.from_private_key_file(
                            self.sftp_key_file, self.sftp_key_file_passphrase)
                    else:
                        # without passphrase
                        key = paramiko.RSAKey.from_private_key_file(
                            self.sftp_key_file)
                    # add disabled_algorithms option
                    disabled_algo_list = []
                    if self.sftp_key_disabled_algorithms:
                        disabled_algo_list = \
                            [alg.strip() for alg in
                             self.sftp_key_disabled_algorithms.split(",")]
                        self._logger.debug("disabled algorithm(s): "
                                           f"{disabled_algo_list}")

                    # connect with pub key
                    ssh.connect(self.sftp_hostname,
                                username=self.sftp_username,
                                pkey=key, timeout=self.sftp_connect_timeout,
                                disabled_algorithms=dict(
                                    pubkeys=disabled_algo_list))
                else:
                    # connect with sftp password
                    ssh.connect(self.sftp_hostname,
                                username=self.sftp_username,
                                password=self.sftp_password,
                                timeout=self.sftp_connect_timeout)

                # create sftp session
                self._session = ssh.open_sftp()

            except Exception as e:
                self._logger.warning("Exception: %s during SFTP connect", e)
                self._session_dt = None
                return None
            if self.sftp_directory != '.':
                try:
                    self._logger.debug("changing directory to %s...",
                                       self.sftp_directory)
                    self._session.chdir(self.sftp_directory)

                except Exception as e:
                    self._logger.warning("Exception: %s during chdir on %s", e,
                                         self.sftp_directory)
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
        stor_name = self.sftp_basename
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
            # put tmp file
            session.put(xaf.filepath, tmp_stor)
        except Exception as e:
            self._logger.warning("Exception: %s during PUT %s" %
                                 (e, tmp_stor))
            return False
        try:
            if self.tmp_suffix != "":
                # rename tmp file and overwrite if already exists
                session.posix_rename(tmp_stor, stor_name)
        except Exception as e:
            self._logger.warning("Exception: %s during RENAME %s %s" %
                                 (e, tmp_stor, stor_name))
            return False
        self.info("%s successfully uploaded to %s:%s/%s" %
                  (xaf.filepath, self.sftp_hostname,
                   self.sftp_directory, stor_name))
        return True

    def _close(self):
        try:
            self._session.close()
        except Exception as e:
            self._logger.debug("can't close sftp connection: %s", e)
        self._session = None
        self._session_dt = None

    def destroy(self):
        self._logger.info("closing sftp session")
        self._close()

    def ping(self):
        # called every second
        if self._session is not None and self._session_dt is not None:
            d = (datetime.datetime.now() - self._session_dt).total_seconds()
            if d > self.sftp_session_lifetime:
                self._logger.info("closing too old sftp session")
                self._close()


if __name__ == "__main__":
    x = SftpSendStep()
    x.run()
