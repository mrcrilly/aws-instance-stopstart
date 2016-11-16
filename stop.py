import boto3
import logging

from croniter import croniter
from datetime import datetime

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    filters = [{
            "Name": "tag-key",
            "Values": ["auto_stop"]
        },
        {
            "Name": "instance-state-name", 
            "Values": ["running"]
        }
    ]
    
    reservations = ec2.describe_instances(Filters=filters)

    if reservations:
        stop_us = []
        for reservation in reservations["Reservations"]:
            if reservation["Instances"]:
                for instance in reservation["Instances"]:
                    for tag in instance["Tags"]:
                        if tag["Key"] == "autoStop":
                            logging.info("Looking at instance %s" % instance["InstanceId"])
                            # The maths here is a bit mental, but here's what happening:

                            # If we assume the current date and time is 2016-11-15 @ 1315
                            # >>> now = datetime(2016, 11, 15, 13, 15)
                            
                            # And based on that date, we manage a cronjob that triggers
                            # at 1310 every Monday through Friday
                            # >>> cron = croniter("10 13 * * MON-FRI", now)
                            
                            # And we calculate the difference between the current date/time
                            # and the PREVIOUS time this cronjob was due to run
                            # >>> diff = now - cron.get_prev(datetime)
                            
                            # And review the difference in seconds (which is five minutes here
                            # because 1315 - 1310 = 5)
                            # >>> diff.seconds
                            # 300

                            # And the difference is <= 300 seconds
                            # >>> diff.seconds <= 300
                            # True
                            
                            # Then the Lambda just passed the due date and should
                            # shutdown/startup the instance

                            try:
                                now = datetime.now()
                                cron = croniter(tag["Value"], now)
                                diff = now - cron.get_prev(datetime)
                                if diff.seconds <= 300:
                                    print "Will shutdown instance %s (%d <= %d = %s)" % (instance["InstanceId"], diff.seconds, 300, diff.seconds <= 300)
                                    stop_us.append(instance["InstanceId"])
                            except:
                                pass

            else:
                logging.info("No instances inside reservation %s" % reservation["ReservationId"])
                
        ec2.stop_instances(InstanceIds=stop_us)
    else:
        logging.info("No reservations found, at all, using given filters.")
