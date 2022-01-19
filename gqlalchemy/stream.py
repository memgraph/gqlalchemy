from kafka import KafkaConsumer as KafkaConsumer_
from time import sleep
from abc import ABC, abstractmethod
import pulsar
import threading


class Consumer(ABC):
    @abstractmethod
    def _consume_with_function(self):
        pass

    def consume_with_function(self, function, sleep_duration):
        t = threading.Thread(target=self._consume_with_function(function, sleep_duration))
        t.start()
        t.join()


class KafkaConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        self.consumer = KafkaConsumer_(*args, **kwargs)

    def _consume_with_function(self, function, sleep_duration):
        continue_loop = True
        while continue_loop:
            msg_pack = self.consumer.poll()
            if not msg_pack:
                sleep(sleep_duration)
                continue
            for _, messages in msg_pack.items():
                for message in messages:
                    try:
                        continue_loop = function(message)
                    except Exception as error:
                        print(error)
                        continue


class PulsarConsumer(Consumer):
    def __init__(self, *args, **kwargs):
        self.client = pulsar.Client(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        self.consumer = self.client.subscribe(*args, **kwargs)

    def _consume_with_function(self, function, sleep_duration):
        continue_loop = True
        while continue_loop:
            msg = self.consumer.receive()
            try:
                continue_loop = function(msg)
                self.consumer.acknowledge(msg)
            except Exception as error:
                self.consumer.negative_acknowledge(msg)
                print(error)
                continue
