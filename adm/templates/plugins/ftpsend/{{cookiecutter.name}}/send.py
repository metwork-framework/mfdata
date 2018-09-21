#!/usr/bin/env python3

import os
import ftplib
import traceback

from acquisition.batch_step import AcquisitionBatchStep


class Step{{cookiecutter.name|capitalize}}Send(AcquisitionBatchStep):

    plugin_name = "{{cookiecutter.name}}"
    step_name = "send"

    def add_extra_arguments(self, parser):
        parser.add_argument('--machine', action='store', default='machine',
                            help='target machine for ftp transfer')
        parser.add_argument('--user', action='store', default='user',
                            help='target user for ftp transfer')
        parser.add_argument('--passwd', action='store', default='passwd',
                            help='target passwd for ftp transfer')
        parser.add_argument('--directory', action='store', default='.',
                            help='target directory for ftp transfer')
        parser.add_argument('--suffix', action='store', default='.t',
                            help='temporary suffix while transferring')
        parser.add_argument('--max-number', action='store', default='100',
                            help='Max number of files before launching' +
                                 ' batch process')
        parser.add_argument('--max-wait', action='store', default='10',
                            help='Max time before launching batch process')
        parser.add_argument('--keep-original-basenames', action='store',
                            default='yes', help='Keep files original'
                            ' basenames on target machine')

    @property
    def batch_process_max_size(self):
        return int(self.args.max_number)

    @property
    def batch_process_max_wait(self):
        return int(self.args.max_wait)

    def warning_ex(self, e, msg):
        self.warning("Exception %s catched during %s execution: %s" %
                     (type(e), msg, traceback.format_exc()))
        return False

    def batch_process(self, xafs):
        try:
            ftp = ftplib.FTP(host=self.args.machine, user=self.args.user,
                             passwd=self.args.passwd, timeout=30)
        except Exception as e:
            return \
                self.warning_ex(e, "Ftp connect failed on %s, "
                                "user %s"
                                % (self.args.machine, self.args.user))
        else:
            self.debug("Connected to %s" % self.args.machine)
        if self.args.directory != '.':
            try:
                ftp.cwd(self.args.directory)
            except Exception as e:
                return \
                    self.warning_ex(e, "Ftp cwd directory %s failed on %s"
                                    % (self.args.directory,
                                       self.args.machine))
        results = []
        for xaf in xafs:
            stor_name = os.path.basename(xaf.filepath)
            if (self.args.keep_original_basenames == 'yes' and
                        self.get_original_basename(xaf) != 'unknown'):
                stor_name = self.get_original_basename(xaf)
            tmp_stor = stor_name + self.args.suffix

            try:
                with open(xaf.filepath, "rb") as f:
                    ftp.storbinary("STOR %s" % tmp_stor, f)
                ftp.rename(tmp_stor, stor_name)
            except Exception as e:
                self.warning_ex(e, "STOR %s failed on %s" %
                                (tmp_stor, self.args.machine))
                results.append(False)
            else:
                self.info("Transfer FTP success file %s on %s" %
                          (xaf.filepath, self.args.machine))
                results.append(True)
        try:
            ftp.quit()
        except Exception as e:
            return self.warning_ex(e, "Can't quit FTP connexion to %s" %
                                   self.args.machine)
        return results


if __name__ == "__main__":
    x = Step{{cookiecutter.name|capitalize}}Send()
    x.run()
