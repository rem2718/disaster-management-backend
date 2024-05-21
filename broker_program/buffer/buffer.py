from decimal import Decimal
import json
import os

import ijson


class Buffer:

    def __init__(self, buffer_path, queue_limit):
        self.buffer_path = buffer_path
        self.queue_limit = queue_limit
        self.buffer_queue = []

    def file_empty(self):
        return not os.path.getsize(self.buffer_path)

    def queue_empty(self):
        return not self.buffer_queue

    def _queue_full(self):
        return len(self.buffer_queue) >= self.queue_limit

    def _buffer_queue_to_file(self):
        buffer_file = open(self.buffer_path, mode="r+")
        if self.file_empty():
            json.dump(self.buffer_queue, buffer_file, indent=4)
        else:
            buffer_file.seek(0, 2)
            position = buffer_file.tell() - 1
            buffer_file.seek(position)
            json_str = json.dumps(self.buffer_queue, indent=4)
            buffer_file.write(f",{json_str[2:]}")
        buffer_file.close()
        self.buffer_queue = []
        print("Buffer queue is written into the file")

    def buffer_to_queue(self, topic, data):
        if self._queue_full():
            self._buffer_queue_to_file()
        item = {
            "topic": topic,
            "data": data,
        }
        self.buffer_queue.append(item)
        print(f"Buffered message: {data['id']}")

    def publish_file(self, client):
        buffer_file = open(self.buffer_path, "r+")
        parser = ijson.items(buffer_file, "item")
        for item in parser:
            topic = item["topic"]
            data = item["data"]
            for key, value in data.items():
                if isinstance(value, Decimal):
                    data[key] = float(value)
            client.publish(topic, payload=json.dumps(data), qos=1)
            print(f"Published message from buffer file: {data['id']}")
        buffer_file.truncate(0)
        buffer_file.close()

    def publish_queue(self, client):
        while not self.queue_empty():
            item = self.buffer_queue.pop(0)
            topic = item["topic"]
            data = item["data"]
            client.publish(topic, payload=json.dumps(data), qos=1)
            print(f"Published message from buffer queue: {data['id']}")
