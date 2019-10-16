import datetime

from acquisition import AcquisitionStep
from mfutil import get_unique_hexa_identifier


class AcquisitionBatch(object):

    id = None
    _start = None
    _xafs = None
    max_size = None
    max_wait = None

    def __init__(self, max_size, max_wait):
        self.id = get_unique_hexa_identifier()
        self._xafs = []
        self.max_size = max_size
        self.max_wait = max_wait

    def append(self, xaf):
        self._xafs.append(xaf)
        if self._start is None:
            self._start = datetime.datetime.utcnow()

    def get_size(self):
        return len(self._xafs)

    def get_age(self):
        if self._start is None:
            return 0
        delta = datetime.datetime.utcnow() - self._start
        return delta.total_seconds()

    def is_ready(self):
        if self.get_size() >= self.max_size:
            return True
        if self.get_age() >= self.max_wait:
            return True
        return False

    def get_xafs(self):
        return self._xafs


class AcquisitionBatchStep(AcquisitionStep):
    """Abstract class to describe a batch acquisition step.

    You have to override this class.

    """

    __batch = None

    def __init__(self):
        super(AcquisitionBatchStep, self).__init__()

    @property
    def batch_process_max_size(self):
        """Return the max size of a batch in batch process mode.

        If not overriden, the default value is 100.

        """
        return 100

    @property
    def batch_process_max_wait(self):
        """Max wait (in seconds) to fill the batch in batch process mode.

        If not overriden, the default value is 10 (so 10 seconds).

        """
        return 10

    @property
    def _batch(self):
        # Lazy init of AcquisitionBatch (to be able to have dynamic
        # batch_process_max_size/batch_process_max_wait)
        if self.__batch is None:
            self.__batch = AcquisitionBatch(self.batch_process_max_size,
                                            self.batch_process_max_wait)
        return self.__batch

    def _reinit_batch(self):
        """Reinit the current batch."""
        self.__batch = None

    def process(self, xaf):
        raise NotImplementedError("process() method should not be called in "
                                  "batch process mode")

    def batch_process(self, xafs):
        """Process a batch of files.

        Process several XattrFile (between 1 and max_batch_size files in one
        call). You have to override this method.

        File are moved into a temporary directory before the call with
        unique filenames. Extended attributes are copied to them.
        So you can do what you want with them.

        If the method returns True:
        - we considerer that the processing is ok
        - all files are deleted if necessary

        If the method returns False:
        - we considerer that the result is False for each file
        - so each file follow the failure policy

        If the method returns an array of booleans (of the same size than
        the xafs array), we consider that the processing status for each file.

        Args:
            xafs (list): XattrFile objects (list of files to process).

        Returns:
            Processing status (True, False or array of booleans).

        """
        raise NotImplementedError("batch_process() method must be overriden "
                                  "in \"batch process mode\"")

    def _destroy(self):
        try:
            if self._batch.get_size():
                # we have a last batch to process
                # let's process it by force
                self._conditional_process_batch(force=True)
        except TypeError:
            pass
        super(AcquisitionBatchStep, self)._destroy()

    def _ping(self, *args, **kwargs):
        self._conditional_process_batch()
        super(AcquisitionBatchStep, self)._ping(*args, **kwargs)

    def _is_batch_ready(self, force=False):
        if force and self._batch.get_size() > 0:
            return True
        return self._batch.is_ready()

    def _before(self, xaf):
        status = super(AcquisitionBatchStep, self)._before(xaf)
        if not status:
            return False
        self._batch.append(xaf)
        self.set_tag(xaf, "batch_id", self._batch.id, add_latest=False)
        self.info("File %s added in batch %s", xaf._original_filepath,
                  self._batch.id)
        return False

    def _conditional_process_batch(self, force=False):
        if self._is_batch_ready(force or self._debug_mode):
            self.debug("Batch %s is ready (size: %i, age: %s seconds) => "
                       "let's process it",
                       self._batch.id, self._batch.get_size(),
                       self._batch.get_age())
            self._process_batch()
            self._reinit_batch()
        else:
            if self._batch.get_size() > 0:
                self.debug("Batch %s is not ready (size: %i, age: %s seconds)",
                           self._batch.id, self._batch.get_size(),
                           self._batch.get_age())

    def _process(self, xaf):
        super(AcquisitionBatchStep, self)._process(xaf)
        self._conditional_process_batch()

    def _process_batch(self):
        self.info("Start the processing of batch %s...", self._batch.id)
        timer = self.get_stats_client().timer("processing_batch_timer")
        timer.start()
        xafs = self._batch.get_xafs()
        size = sum([x.getsize() for x in xafs])
        process_status = \
            self._exception_safe_call(self.batch_process, [xafs], {},
                                      "batch_process", False)
        after_status = self._after_batch(xafs, process_status)
        self.get_stats_client().incr("number_of_processed_files", len(xafs))
        self.get_stats_client().incr("bytes_of_processed_files", size)
        self.get_stats_client().incr("number_of_processed_batches", 1)
        timer.stop()
        self.info("End of the processing of batch %s...", self._batch.id)
        if not after_status:
            self.get_stats_client().incr("number_of_processed_"
                                         "batches_error", 1)
            self.warning("Bad processing status for batch: %s", self._batch.id)

    def _after_batch(self, xafs, process_status):
        if process_status is None:
            process_status = False
        if isinstance(process_status, bool):
            for xaf in xafs:
                super(AcquisitionBatchStep, self)._after(xaf, process_status)
            return process_status
        else:
            if len(process_status) != len(xafs):
                self.warning("bad process status len(process_status) = %i "
                             "which is different than len(xafs) = %i" %
                             (len(process_status), len(xafs)))
                super(AcquisitionBatchStep, self)._after(xaf, False)
                return False
            for (xaf, pstatus) in zip(xafs, process_status):
                super(AcquisitionBatchStep, self)._after(xaf, pstatus)
            return min(process_status)
