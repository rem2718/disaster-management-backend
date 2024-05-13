class Stack:
    def __init__(self, capacity):
        self.stack = []
        self.capacity = capacity

    def push(self, item):
        if len(self.stack) == self.capacity:
            self.stack.pop(0)
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            print("Stack is empty.")

    def back(self):
        self.pop()
        return self.pop()

    def is_empty(self):
        return len(self.stack) == 0

    def cur(self):
        if self.is_empty():
            return None
        return self.stack[-1]

    def prev(self):
        if self.size() < 2:
            return None
        return self.stack[-2]

    def size(self):
        return len(self.stack)

    def __str__(self):
        return "[" + " ".join(map(str, self.stack)) + "]"
