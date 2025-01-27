# Advanced Post-installation Tasks

This page explains some advanced tasks and configuration options that can be performed after the bot installation and may be uselful in some environments.

If you do not know what things mentioned here mean, you probably do not need it.

## Running multiple instances of Tradescope

This section will show you how to run multiple bots at the same time, on the same machine.

### Things to consider

* Use different database files.
* Use different Telegram bots (requires multiple different configuration files; applies only when Telegram is enabled).
* Use different ports (applies only when Tradescope REST API webserver is enabled).

### Different database files

In order to keep track of your trades, profits, etc., tradescope is using a SQLite database where it stores various types of information such as the trades you performed in the past and the current position(s) you are holding at any time. This allows you to keep track of your profits, but most importantly, keep track of ongoing activity if the bot process would be restarted or would be terminated unexpectedly.

Tradescope will, by default, use separate database files for dry-run and live bots (this assumes no database-url is given in either configuration nor via command line argument).
For live trading mode, the default database will be `tradesv3.sqlite` and for dry-run it will be `tradesv3.dryrun.sqlite`.

The optional argument to the trade command used to specify the path of these files is `--db-url`, which requires a valid SQLAlchemy url.
So when you are starting a bot with only the config and strategy arguments in dry-run mode, the following 2 commands would have the same outcome.

``` bash
tradescope trade -c MyConfig.json -s MyStrategy
# is equivalent to
tradescope trade -c MyConfig.json -s MyStrategy --db-url sqlite:///tradesv3.dryrun.sqlite
```

It means that if you are running the trade command in two different terminals, for example to test your strategy both for trades in USDT and in another instance for trades in BTC, you will have to run them with different databases.

If you specify the URL of a database which does not exist, tradescope will create one with the name you specified. So to test your custom strategy with BTC and USDT stake currencies, you could use the following commands (in 2 separate terminals):

``` bash
# Terminal 1:
tradescope trade -c MyConfigBTC.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesBTC.dryrun.sqlite
# Terminal 2:
tradescope trade -c MyConfigUSDT.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesUSDT.dryrun.sqlite
```

Conversely, if you wish to do the same thing in production mode, you will also have to create at least one new database (in addition to the default one) and specify the path to the "live" databases, for example:

``` bash
# Terminal 1:
tradescope trade -c MyConfigBTC.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesBTC.live.sqlite
# Terminal 2:
tradescope trade -c MyConfigUSDT.json -s MyCustomStrategy --db-url sqlite:///user_data/tradesUSDT.live.sqlite
```

For more information regarding usage of the sqlite databases, for example to manually enter or remove trades, please refer to the [SQL Cheatsheet](sql_cheatsheet.md).

### Multiple instances using docker

To run multiple instances of tradescope using docker you will need to edit the docker-compose.yml file and add all the instances you want as separate services. Remember, you can separate your configuration into multiple files, so it's a good idea to think about making them modular, then if you need to edit something common to all bots, you can do that in a single config file. 
``` yml
---
version: '3'
services:
  tradescope1:
    image: khulnasoft/tradescope:stable
    # image: khulnasoft/tradescope:develop
    # Use plotting image
    # image: khulnasoft/tradescope:develop_plot
    # Build step - only needed when additional dependencies are needed
    # build:
    #   context: .
    #   dockerfile: "./docker/Dockerfile.custom"
    restart: always
    container_name: tradescope1
    volumes:
      - "./user_data:/tradescope/user_data"
    # Expose api on port 8080 (localhost only)
    # Please read the https://www.tradescope.io/en/latest/rest-api/ documentation
    # before enabling this.
     ports:
     - "127.0.0.1:8080:8080"
    # Default command used when running `docker compose up`
    command: >
      trade
      --logfile /tradescope/user_data/logs/tradescope1.log
      --db-url sqlite:////tradescope/user_data/tradesv3_tradescope1.sqlite
      --config /tradescope/user_data/config.json
      --config /tradescope/user_data/config.tradescope1.json
      --strategy SampleStrategy
  
  tradescope2:
    image: khulnasoft/tradescope:stable
    # image: khulnasoft/tradescope:develop
    # Use plotting image
    # image: khulnasoft/tradescope:develop_plot
    # Build step - only needed when additional dependencies are needed
    # build:
    #   context: .
    #   dockerfile: "./docker/Dockerfile.custom"
    restart: always
    container_name: tradescope2
    volumes:
      - "./user_data:/tradescope/user_data"
    # Expose api on port 8080 (localhost only)
    # Please read the https://www.tradescope.io/en/latest/rest-api/ documentation
    # before enabling this.
    ports:
      - "127.0.0.1:8081:8080"
    # Default command used when running `docker compose up`
    command: >
      trade
      --logfile /tradescope/user_data/logs/tradescope2.log
      --db-url sqlite:////tradescope/user_data/tradesv3_tradescope2.sqlite
      --config /tradescope/user_data/config.json
      --config /tradescope/user_data/config.tradescope2.json
      --strategy SampleStrategy

```
You can use whatever naming convention you want, tradescope1 and 2 are arbitrary. Note, that you will need to use different database files, port mappings and telegram configurations for each instance, as mentioned above. 


## Configure the bot running as a systemd service

Copy the `tradescope.service` file to your systemd user directory (usually `~/.config/systemd/user`) and update `WorkingDirectory` and `ExecStart` to match your setup.

!!! Note
    Certain systems (like Raspbian) don't load service unit files from the user directory. In this case, copy `tradescope.service` into `/etc/systemd/user/` (requires superuser permissions).

After that you can start the daemon with:

```bash
systemctl --user start tradescope
```

For this to be persistent (run when user is logged out) you'll need to enable `linger` for your tradescope user.

```bash
sudo loginctl enable-linger "$USER"
```

If you run the bot as a service, you can use systemd service manager as a software watchdog monitoring tradescope bot 
state and restarting it in the case of failures. If the `internals.sd_notify` parameter is set to true in the 
configuration or the `--sd-notify` command line option is used, the bot will send keep-alive ping messages to systemd 
using the sd_notify (systemd notifications) protocol and will also tell systemd its current state (Running or Stopped) 
when it changes. 

The `tradescope.service.watchdog` file contains an example of the service unit configuration file which uses systemd 
as the watchdog.

!!! Note
    The sd_notify communication between the bot and the systemd service manager will not work if the bot runs in a Docker container.

## Advanced Logging

On many Linux systems the bot can be configured to send its log messages to `syslog` or `journald` system services. Logging to a remote `syslog` server is also available on Windows. The special values for the `--logfile` command line option can be used for this.

### Logging to syslog

To send Tradescope log messages to a local or remote `syslog` service use the `--logfile` command line option with the value in the following format:

* `--logfile syslog:<syslog_address>` -- send log messages to `syslog` service using the `<syslog_address>` as the syslog address.

The syslog address can be either a Unix domain socket (socket filename) or a UDP socket specification, consisting of IP address and UDP port, separated by the `:` character.

So, the following are the examples of possible usages:

* `--logfile syslog:/dev/log` -- log to syslog (rsyslog) using the `/dev/log` socket, suitable for most systems.
* `--logfile syslog` -- same as above, the shortcut for `/dev/log`.
* `--logfile syslog:/var/run/syslog` -- log to syslog (rsyslog) using the `/var/run/syslog` socket. Use this on MacOS.
* `--logfile syslog:localhost:514` -- log to local syslog using UDP socket, if it listens on port 514.
* `--logfile syslog:<ip>:514` -- log to remote syslog at IP address and port 514. This may be used on Windows for remote logging to an external syslog server.

Log messages are send to `syslog` with the `user` facility. So you can see them with the following commands:

* `tail -f /var/log/user`, or 
* install a comprehensive graphical viewer (for instance, 'Log File Viewer' for Ubuntu).

On many systems `syslog` (`rsyslog`) fetches data from `journald` (and vice versa), so both `--logfile syslog` or `--logfile journald` can be used and the messages be viewed with both `journalctl` and a syslog viewer utility. You can combine this in any way which suites you better.

For `rsyslog` the messages from the bot can be redirected into a separate dedicated log file. To achieve this, add

```
if $programname startswith "tradescope" then -/var/log/tradescope.log
```

to one of the rsyslog configuration files, for example at the end of the `/etc/rsyslog.d/50-default.conf`.

For `syslog` (`rsyslog`), the reduction mode can be switched on. This will reduce the number of repeating messages. For instance, multiple bot Heartbeat messages will be reduced to a single message when nothing else happens with the bot. To achieve this, set in `/etc/rsyslog.conf`:

```
# Filter duplicated messages
$RepeatedMsgReduction on
```

### Logging to journald

This needs the `cysystemd` python package installed as dependency (`pip install cysystemd`), which is not available on Windows. Hence, the whole journald logging functionality is not available for a bot running on Windows.

To send Tradescope log messages to `journald` system service use the `--logfile` command line option with the value in the following format:

* `--logfile journald` -- send log messages to `journald`.

Log messages are send to `journald` with the `user` facility. So you can see them with the following commands:

* `journalctl -f` -- shows Tradescope log messages sent to `journald` along with other log messages fetched by `journald`.
* `journalctl -f -u tradescope.service` -- this command can be used when the bot is run as a `systemd` service.

There are many other options in the `journalctl` utility to filter the messages, see manual pages for this utility.

On many systems `syslog` (`rsyslog`) fetches data from `journald` (and vice versa), so both `--logfile syslog` or `--logfile journald` can be used and the messages be viewed with both `journalctl` and a syslog viewer utility. You can combine this in any way which suites you better.
