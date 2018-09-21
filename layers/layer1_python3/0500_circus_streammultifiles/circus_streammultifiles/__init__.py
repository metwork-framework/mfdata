from circus.stream import FileStream
import psutil
from mflog import getLogger

log = getLogger("circus_streammultifiles")


class MultiFilesStream(FileStream):

    _filename = None
    _time_format = None
    _numprocesses = None

    # dict pid => (slot number, opened FileStream)
    _slots = None

    def clean_old_pids(self):
        pids = list(self._slots.keys())
        for pid in pids:
            if not psutil.pid_exists(pid):
                slot_number, file_stream = self._slots[pid]
                file_stream.close()
                del(self._slots[pid])

    def pid_to_slot_number_stream(self, pid):
        if pid in self._slots:
            return self._slots[pid]
        self.clean_old_pids()
        used_slot_numbers = [x[0] for x in self._slots.values()]
        for i in range(0, self._numprocesses):
            if i not in used_slot_numbers:
                fn = self._filename.replace('{SLOT}', str(i))
                stream = FileStream(filename=fn, time_format=self._time_format)
                stream.open()
                self._slots[pid] = (i, stream)
                return (i, stream)
        log.warning("can't find a slot number for pid=%i" % pid)
        return (None, None)

    def __init__(self, filename=None, time_format=None, **kwargs):
        self._numprocesses = int(kwargs.get('numprocesses', '1'))
        self._slots = {}
        self._filename = filename
        self._time_format = time_format

    def _should_rollover(self, raw_data):
        return False

    def open(self):
        pass

    def close(self):
        for stream in [x[1] for x in self._slots.values()]:
            stream.close()
        self._slots = {}

    def write_data(self, data):
        pid = data.get('pid', None)
        if pid is None:
            log.warning("can't get the pid for data = %s => not logging" %
                        data)
            return
        slot_number, stream = self.pid_to_slot_number_stream(pid)
        if slot_number is None or stream is None:
            return
        stream.write_data(data)
