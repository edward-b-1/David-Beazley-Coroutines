
from .task import Task

from .scheduler_interface import IScheduler
from .systemcall_interface import ISystemCall


class SystemCall(ISystemCall):

    def handle():
        pass


class NullSystemCall(SystemCall):

    def __init__(self) -> None:
        super().__init__()

    def handle(self):
        pass


class NewTask(SystemCall):

    def __init__(self, name:str, target):
        if not isinstance(name, str):
            raise TypeError(f'name must be of type str, not {type(name)}')

        super().__init__()
        self.name = name
        self.target = target

    def handle(self):
        print(f'>>>> called NewTask.handle')
        task_id = self.scheduler.new_task(self.name, self.target)
        self.task.sendval = task_id
        self.scheduler.schedule(self.task)


class GetTaskId(SystemCall):

    def handle(self):
        self.task.sendval = self.task.get_task_id()
        self.scheduler.schedule(self.task)


class KillTask(SystemCall):

    def __init__(self, task_id):
        if not isinstance(task_id, int):
            print(f'task_id must be of type int, not {type(task_id)}')
        self.task_id = task_id

    def handle(self):
        task = self.scheduler.task_map.get(self.task_id, None)

        if task:
            task.target.close()
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.scheduler.schedule(self.task)


class WaitTask(SystemCall):

    def __init__(self, task_id) -> None:
        if not isinstance(task_id, int):
            print(f'task_id must be of type int, not {type(task_id)}')
        self.task_id = task_id

    def handle(self):
        result = self.scheduler.wait_for_exit(self.task, self.task_id)
        self.task.sendval = result

        if not result:
            self.scheduler.schedule(self.task)


class AcceptWait(SystemCall):

    def __init__(self, fd) -> None:
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        super().__init__()
        self.fd = fd


class ReadWait(SystemCall):

    def __init__(self, fd) -> None:
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        super().__init__()
        self.fd = fd

    def handle(self):
        print(f'handle ReadWait: {self.fd}')
        fd = self.fd
        self.scheduler.wait_for_read(self.task, fd)


class WriteWait(SystemCall):

    def __init__(self, fd) -> None:
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        super().__init__()
        self.fd = fd

    def handle(self):
        self.scheduler.wait_for_write(self.task, self.fd)


class Sleep(SystemCall):

    def __init__(self, timeout) -> None:
        if not isinstance(timeout, float):
            print(f'timeout must be of type float, not {type(timeout)}')
        super().__init__()
        self.timeout = timeout

    def handle(self):
        self.scheduler.wait_for_timeout(self.task, self.timeout)
