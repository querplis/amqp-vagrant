#!/usr/bin/env python3
import configparser
import pika
import sys
import os
import time

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def main():
    config=configparser.RawConfigParser()
    config.read('app.cfg')
    ampq_host=config.get('app', 'ampq_host')
    ampq_queuename=config.get('app', 'ampq_queuename')

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ampq_host))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=ampq_queuename)

    def callback(ch, method, properties, body):
        if is_intstring(body):
            print(" [x] Sleeping {} seconds".format(int(body)))
            for i in range(1, int(body)+1):
                time.sleep(1)
                print(i, end=' ', flush=True)
        else:
            print(" [x] Received {}".format(
                body.decode()), end=' ', flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)

        print('\n [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_consume(
        queue=ampq_queuename, on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
