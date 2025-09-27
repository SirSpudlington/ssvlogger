# SSV logger

A simple tool to make the SSV node's logs easier to view.

## Dependencies

- Python3
- [Colorama](https://pypi.org/project/colorama/)

## Installation

```bash
python3 -m pip install ssvlogger
```

## How to use

In both cases omit the `-f` to process all available logs, not just follow the current logs.

### With docker

`docker logs -f ssv_node | ssvlogger`

### Without docker

If you do not use docker it will only work as a service, assuming you have a service called "ssv_node" you should run
`journalctl -u ssv_node -f | ssvlogger -j`

Or you could use:

`journalctl -u ssv_node -f --output cat | ssvlogger`

### Directly on the log file

If you specify `ssvlogger [FILE]` the script will attempt to read the file instead of using journalctl or docker.

## Additional Flags

You can also use different flags to disable or enable certain features in the script

|short command|long command|description|
|-|-|-|
|**-n**|--no-spam|Disables connection and registry event logs
|**-t**|--traceback|Shows tracebacks for errors
|**-j**|--journal|
