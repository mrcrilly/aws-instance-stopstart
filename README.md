# AWS Instance Auto Stop/Start
Automatically stops/starts instances based on an EC2 tag on the instance(s).

## Process
1. Scan through all EC2 instances in the configured region, filtering on a specific tag;
1. Take the value of the tag, which should be a cronjob;
1. Determine when the **previous run** on that cronjob should have taken place, relative to the current date/time;
1. If it was within the last five minutes, then perform the stop/start action;
1. If not, then ignore the instance and take no action.

## Cronjob Logic
The maths is a bit mental, but here's what happening:

If we assume the current date and time is `2016-11-15 @ 1315`:

```
>>> now = datetime(2016, 11, 15, 13, 15)
```

And based on that date, we manage a cronjob that triggers at 1310 every Monday through Friday:

```
>>> cron = croniter("10 13 * * MON-FRI", now)
```

And we calculate the difference between the current date/time and the PREVIOUS time this cronjob was due to run:

```
>>> diff = now - cron.get_prev(datetime)
```

And review the difference in seconds (which is five minutes here because `1315 - 1310 = 5`):

```
>>> diff.seconds
300
```

And the difference is `<= 300` seconds:

```
>>> diff.seconds <= 300
True
```

Then the Lambda just passed the due date and should shutdown/startup the instance.
