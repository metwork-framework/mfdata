.. index:: log, logger, logging, mflog
# MFDATA Log

## Default logs files
MFDATA produces logs files stored in the `log` directory of the MFDATA root directory.

Logs parameters as log retention, log level are configured in the [log] section of the `config/config.ini` file in the MFDATA root directory. Check this file for further details.

Each MFDATA plugin has its own logs files:

- step_{plugin_name}_{step_name}.stdout
- step_{plugin_name}_{step_name}.stderr

The `.sddout` file contains `INFO` and `DEBUG` level logs. The `.stderr` file contains `WARNING`, `ERROR` and `CRITICAL`.

When you want to log data from a MFDATA plugin class whose base class is  :py:class:`AcquisitionStep <acquisition.step.AcquisitionStep>`, you just have to call one of the implemented methods:
```python
self.info(...)
self.debug(...)
self.warning(...)
self.error(...)
self.error_and_die(...)
self.critical(...)
self.exception(...)
```

Check :py:class:`AcquisitionStep <acquisition.step.AcquisitionStep>` for more details.

## Custom logs files

### Classic Python logger
You may want to create your own additional logs files to log specific data and store it in the MFDATA `log` directory. In order to do this, you could create a specific logger as shown below:

```python
import logging
import logging.config
import os


def configure_logger(name, log_name):
    """
    Defines the logger configuration
    :param name: The logger name
    :param log_name: The log file name
    :return: the logger instance
    """
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '%(asctime)s;%(name)8s;%(levelname)s;%(message)s',
                        'datefmt': '%m/%d/%Y %H:%M:%S'}
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': log_name,
                'encoding': 'utf-8',
                'maxBytes': 10485760,
                'backupCount': 3
            },
        },
        'loggers': {
            'ingestion.performance': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True
            },
        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(name)


# Get the MFDATA root directory
basedir = os.environ.get("MODULE_RUNTIME_HOME",
                         os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# Get the MFDATA log directory
log_folder = os.path.abspath(os.path.join(basedir, 'log'))
# create log folder if it doesn't exits
if not os.path.exists(log_folder):
    try:
        os.makedirs(log_folder, exist_ok=True)
    except OSError as err:
        # change the log folder to be the current folder
        log_folder = basedir

my_logger = configure_logger('mya_logger_name', log_name=os.path.join(log_folder, 'my_log_file_name.log'))

```

Then you can call your logger:
```python
my_logger.info(...)
my_logger.debug(...)
my_logger.warning(...)
my_logger.error(...)
my_logger.critical(...)
my_logger.exception(...)
```

### Metwork MFLOG logger

You may also use the 'structured' Metwork MFLOG logger. Check [Metwork MFLOG](https://github.com/metwork-framework/mflog) for more details and example.
