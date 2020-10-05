#!/usr/bin/env python3
import pika
import sys
import configparser

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main(body):
    config=configparser.RawConfigParser()
    config.read('app.cfg')
    ampq_host=config.get('app', 'ampq_host')
    ampq_queuename=config.get('app', 'ampq_queuename')

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ampq_host))
    channel = connection.channel()

    channel.queue_declare(queue=ampq_queuename)

    channel.basic_publish(exchange='', routing_key=ampq_queuename, body=body)
    print(" [x] Sent {body}".format(body=body))
    connection.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("we accept single argument only!\n please run: {} <payload>".format(sys.argv[0]))
        sys.exit(1)
    else:
        body=sys.argv[1]
        main(body)
