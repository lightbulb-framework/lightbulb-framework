from threading import Thread
from threading import Condition


class PipeParent():
    def __init__(self):
        self.condition_A = Condition()
        self.data_A = []
        self.condition_B = Condition()
        self.data_B = []


class PipeImpl():

    def __init__(self, pipe_parent, pipe_id):
        self.pipe_parent = pipe_parent
        self.pipe_id = pipe_id

    def send(self, data):
        if self.pipe_id == 1:
            with self.pipe_parent.condition_B:
                self.pipe_parent.data_B.append(data)
                self.pipe_parent.condition_B.notifyAll()
        elif self.pipe_id == 2:
            with self.pipe_parent.condition_A:
                self.pipe_parent.data_A.append(data)
                self.pipe_parent.condition_A.notifyAll()

    def recv(self):
        if self.pipe_id == 1:
            with self.pipe_parent.condition_A:
                if len(self.pipe_parent.data_A) == 0:
                    self.pipe_parent.condition_A.wait()
                return self.pipe_parent.data_A.pop(0)
        elif self.pipe_id == 2:
            with self.pipe_parent.condition_B:
                if len(self.pipe_parent.data_B) == 0:
                    self.pipe_parent.condition_B.wait()
                return self.pipe_parent.data_B.pop(0)

    def close(self):
        pass

def Pipe():
    pipe_parent = PipeParent()
    pipe_A = PipeImpl(pipe_parent, 1)
    pipe_B = PipeImpl(pipe_parent, 2)
    return pipe_A, pipe_B


