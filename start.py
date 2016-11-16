import boto3
import logging

from croniter import croniter
from datetime import datetime

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    filters = [{
            "Name": "tag-key",
            "Values": ["autoStart"]
        },
        {
            "Name": "instance-state-name", 
            "Values": ["stopped"]
        }
    ]
    
    reservations = ec2.describe_instances(Filters=filters)

    if reservations:
        start_us = []
        for reservation in reservations["Reservations"]:
            if reservation["Instances"]:
                for instance in reservation["Instances"]:
                    for tag in instance["Tags"]:
                        if tag["Key"] == "autoStart":
                            logging.info("Looking at instance %s" % instance["InstanceId"])

                            try:
                                now = datetime.now()
                                cron = croniter(tag["Value"], now)
                                diff = now - cron.get_prev(datetime)
                                if diff.seconds <= 300:
                                    print "Will start instance %s (%d <= %d = %s)" % (instance["InstanceId"], diff.seconds, 300, diff.seconds <= 300)
                                    start_us.append(instance["InstanceId"])
                            except:
                                pass

            else:
                logging.info("No instances inside reservation %s" % reservation["ReservationId"])

        ec2.start_instances(InstanceIds=start_us)
    else:
        logging.info("No reservations found, at all, using given filters.")
