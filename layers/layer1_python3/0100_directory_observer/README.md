# WARNING : NOT READY AT ALL!!!

# directory_observer

`directory_observer` is a tool that allows you to monitor activity on various directories and push the corresponding events to a Redis queue (a list). For example, you may create a file inside one of your monitored directories, the creation event will be pushed to the Redis queue.

## Usage

In order to use `directory_observer`, you will need a configuration file to define the monitored directories and the Redis server. To launch the module, you will need to execute `directory_observer.py` once you launched a Redis server. This operation initializes the logging system and loads the configuration for the monitors. As the initialization can be a bit lengthy, it is recommended that you use `sleep 1` after starting the initialization if you launch `directory_observer` as a background process through a script. This will ensure that `directory_observer` is fully initialized and operational. The monitoring stops when the process receives a SIGTERM.

    python directory_observer.py --config=configfile [--log=logfile]

Once running, the monitor reacts to file creations and file movement/renaming inside of the monitored directories. It also detects movement, renaming and deletion of the monittored directories themselves. All of the events concerning the content of the monitored directories are pushed to the Redis queue. The operations are logged to stdout by default, and can be logged to a log file using `--log`. For more details, use `--help`.

### Configuration file
The config file `directory_observer.ini` defines multiple parameters for the directory observer. In this file, you can define the name of the queue, various Redis and monitorring parameters. Here is a sample file describing the roles of each configurable parameter :

    [common]

    # Defines whether or not a directory should be scrutinized
    # Presence: OPTIONAL (false by default)
    #
    active=false

    # Forced scan interval of a directory in seconds. (0 = No forced scan)
    # In order to "boot the pump" at the start of the process, the active directories are 
    # "listed" and the files actually present and complying with the filter criteria at 
    # this time are indicated in their respective Redis queues.
    # This forced listing operation is repeated every forced_poll seconds, in order to 
    # avoid as much as possible leaving "orphaned files" due to momentary failure of the
    # Redis server or unscrupulous consumer clients. It is therefore possible for clients
    # to receive more than one notification of presence for the same file. It is their responsibility to deal with this eventuality.
    # This value may be different for each directory.
    # Presence: OPTIONAL ((0 = No forced scan) default)
    #
    forced_poll=300

    # Limitation forced scan (0 = No limitation)
    # If the size of a Redis queue is greater than this limit,
    # the polling no longer inserts a notification of presence.
    # Presence: OPTIONAL (10000 by default)
    #
    poll_queue_limit=10000

    ##########################################################################
    # WARNING: 1 single and same value per timeout for all the active queues #
    ##########################################################################
    # The durations that have elapsed since the creation of the WatchMonitor
    # and since the reception of the last event are regularly tested.
    # If one of these 2 values exceeds the following constants, the WatchMonitor
    # is stopped, and a new one is created, activated and takes its place.
    # These timeouts were introduced following the discovery of blockages of
    # the first version of directory_observer based on the GAMIN lib sometimes
    # occurring after a week of smooth operation. (No more directory change notification)
    # Value of application security timeout
    #(Maximum inactivity time (no event reception) before considering the need
    # to stop the application completely)
    # Unlike the "monitor_event" timer, the "monitor_inactivity" timer is not
    # reset in case of a "recreation" of the WatchMonitor
    # Value in seconds (<= 0 -> no timeout)
    # Presence: OPTIONAL (default 300 -> 5 minutes)
    #
    monitor_inactivitytimeout=300


    #################################################################
    # WARNING: 1 single and same Redis server for all active queues #
    #################################################################

    # Name or IP address of the Redis server
    # Presence: MANDATORY
    #
    Redis_server=127.0.0.1

    # Redis server port number
    # Presence: MANDATORY
    #
    Redis_port=8080

    # Value of the Redis security timeout in seconds to avoid interminable
    # blockages during unavailability.
    # Do not set too low a value -> if not Redis events
    # 0 = no timeout (not recommended)))
    # Presence: OPTIONAL ( default 10 )
    #
    timeout=10

    # Regular expressions (list separated by ';') specifying file name patterns
    # to be ignored
    # Note that regardless of the value set, the regular expression
    # "^. * \ Working $" (all files that end in .working) will be added to the list
    # of ignored files. In addition, any subdirectories are totally ignored.
    # Presence: OPTIONAL (^.*\.working$ by default)
    #
    ignore=^.*\.t$;^.*\.tmp$;^.*\.[0-9][0-9]$;^.*\.[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$

    # Regular expressions (a list separated by ';') specifying filename patterns to take
    # into account (ie if the name does not match one of its regular expressions,
    # it will be ignored)
    # Presence: OPTIONAL	(^.*$ by default)
    #
    only=^.*$

    ######################################################################################

    [stage1:common]
    active=true
    directory=dir/stage1
    queue=queue:stage1
    counter=counter:stage1

    [stage2:common]
    active=true
    directory=dir/stage2
    queue=queue:stage2
    counter=counter:stage2

`directory_observer.ini` uses `configparser_extended` which allows for easier configuration. You can find some documentation [here](https://github.com/thefab/configparser_extended). Here, `[stage1:common]` means that this section inherits from the `[common]` section (it gets all the keys from `[common]` as well as those defined in `[stage1:common]`).

In each sections after the line of `#`, there are 4 configuration keys which allow you to set differents parameters :
- `active` : As described in the config file, defines whether or not a directory should be scrutinized
- `directory` : Defines which directory is monitored
- `queue` : Defines the name of the queue where the events will be pushed.
- `counter` : Defines the name of the counter that counts how many event are in the queue.

In the file above, there are 2 sections, each associated to 2 seperate directories. Each have their own queue and counter, which means that events happening in `dir/stage1` will be in `queue:stage1` while events happening in `dir/stage1` will be in `queue:stage1`.


## Details about how the monitoring works

`directory_observer` uses `pynotify` to monitor the events.

### Operations inside the monitored directory

Once you started monitoring your directories, any creation, renaming or movement to the monitored directory will be noticed and pushed to the queue. All these events are handled the same way, there are no distinction between creating a file in the directory, moving a file to the directory or renaming a file in the directory. They are all considered as `created` events. The creation, renaming and movement of sub-directories inside the monitored directories are handled the same way as with files. Keep in mind that the content of the sub-directories is not monitored unless explicitly defined.

In Redis, the events are pushed to a key whose value is a list. The key name is set in the `directory_observer.ini` configuration file, it's the `queue` configuration key.

Concerning the values that are pushed to these queues, they are pushed as JSON files. These values follow the pattern below :

    { 'directory' : dir,
      'filename' : filename,
      'event' : evid,
      'event_timestamp' : time }

- `directory` corresponds to the monitored directory in which the event happened.
- `filename` corresponds to the file which created the event (the file which was created, moved or renamed).
- `event` corresponds to the associated event. As mentionned above, both file creation, movement and renaming are associated with the `created` event.
- `event_timestamp` corresponds to the time at which the event happened.


### Opearations on the monitored directory themselves

If you decide to rename, move or delete a monitored directory, the monitoring on the concerned directory will actually stop. Because `directory_observer` was told to monitor a specific path (to the monitored directory), if the path changes and is not valid anymore (if the directory is moved, renamed or deleted), `directory_observer` will stop monitoring this directory.

