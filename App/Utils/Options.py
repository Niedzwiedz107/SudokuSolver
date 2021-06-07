class MyOptions:
    def __init__(self):
        self.algorithm = "naive"
        self.capture = "offline"

    def get_algorithm_mode(self):
        return self.algorithm

    def get_capture_mode(self):
        return self.capture

    def set_algorithm_mode(self, mode):
        self.algorithm = mode

    def set_capture_mode(self, mode):
        self.capture = mode
