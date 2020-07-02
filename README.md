# craigslist_notify
Termux & python bot for craigslist alerts.

## installation 

Install the [Termux](https://f-droid.org/en/packages/com.termux/) terminal emulator from F-Droid. 

Then, open the shell and install dependencies and `craigslist_notify`:

```shell script
$ pkg install termux-api openssl libxml2 libxslt
$ pip install https://www.github.com/rwev/craigslist_notify/archive/master.zip
```

## configuration

Execution requires a configuration file in the user home directory, `~/.craigslist_notify_config.yaml`.

Specify each search to run as an item in list, with the following fields: 

```yaml
- region: '<REGION>' # region to search, as appears in query subdomain, eg. <REGION>.craiglist.org
  query: '<QUERY>' # string as you would enter in search box
  by: 'OWNER' # | 'DEALER' | 'ALL'  
- region: '<REGION>' 
  query: '<QUERY>' 
  by: 'OWNER'
```

## demo

Install and run:
<br>
<img src="https://raw.githubusercontent.com/rwev/craigslist_notify/master/jpg/run.jpg" height="600px"/>

Receive notifications: 
<br>
<img src="https://raw.githubusercontent.com/rwev/craigslist_notify/master/jpg/notifications.jpg" height="600px"/>

Open links:
<br>
<img src="https://raw.githubusercontent.com/rwev/craigslist_notify/master/jpg/link.jpg" height="600px"/>

Upon completion, the script additionally schedules a job to run itself again on 15 minute intervals.


## TODO
- add support for more search parameters


