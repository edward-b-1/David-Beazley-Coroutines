

from queue import Queue
from queue import PriorityQueue

from select import select

from .task import Task

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from time import time
from time import sleep

from lib_consume import consume

from .scheduler_interface import IScheduler
from .systemcall_interface import ISystemCall


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)


class Scheduler(IScheduler):

    def __init__(self) -> None:
        self.ready_queue = Queue()
        self.task_map = {}

        self.exit_waiting = {}
        self.read_waiting = {}
        self.write_waiting = {}
        self.timeout_waiting = PriorityQueue()

    def new_task(self, name:str, target) -> int:
        if not isinstance(name, str):
            raise TypeError(f'name must be of type str, not {type(name)}')

        task = Task(name, target)
        self.task_map[task.get_task_id()] = task
        self.schedule(task)
        return task.get_task_id()

    def exit(self, task):
        print(f'Task {task.get_task_id()} terminate')
        del self.task_map[task.get_task_id()]

        for task in self.exit_waiting.pop(task.get_task_id(), []):
            self.schedule(task)

    def wait_for_exit(self, task, wait_id):
        if wait_id in self.task_map:
            self.exit_waiting.setdefault(wait_id, []).append(task)
            return True
        else:
            return False

    def wait_for_read(self, task, fd):
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        if not isinstance(task, Task):
            raise TypeError(f'task must be of type Task, not {type(task)}')
        self.read_waiting[fd] = task

    def wait_for_write(self, task, fd):
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        if not isinstance(task, Task):
            raise TypeError(f'task must be of type Task, not {type(task)}')
        self.write_waiting[fd] = task

    def wait_for_timeout(self, task, timeout):
        now = time()
        expire_time = now + timeout
        queue_item = PrioritizedItem(priority=expire_time, item=task)
        self.timeout_waiting.put_nowait(queue_item)

    def get_min_timeout_from_priority_queue(self, now:float) -> float|None:
        if not self.timeout_waiting.empty():
            queue_item = self.timeout_waiting.get_nowait()
            expire_time = queue_item.priority
            remaining_time = expire_time - now
            self.timeout_waiting.put_nowait(queue_item)
            return remaining_time
        else:
            return None

    def io_poll(self, timeout):
        print(f'io_poll: timeout={timeout}')
        now = time()

        if not self.timeout_waiting.empty():
            print(f'timeout waiting is not empty')
            queue_item = self.timeout_waiting.get_nowait()
            expire_time = queue_item.priority
            print(f'time until expire: {expire_time - now}')

            if now > expire_time:
                task = queue_item.item
                self.schedule(task)
                return
            else:
                self.timeout_waiting.put_nowait(queue_item)

        min_timeout = self.get_min_timeout_from_priority_queue(now)

        if timeout is None:
            timeout = min_timeout
            # does not matter if min_timeout is also none

        print(f'timeout: {timeout}')

        if self.read_waiting or self.write_waiting:
            print('there is something read waiting or write waiting')

            print(f'read_waiting')
            for k, v in self.read_waiting.items():
                print(f'  {k} -> {v}')

            print(f'write waiting')
            for k, v in self.write_waiting.items():
                print(f'  {k} -> {v}')

            r, w, _ = select(
                self.read_waiting,
                self.write_waiting,
                [],
                timeout,
            )

            # if len(r) > 0:
            #     print(f'read ready:')
            #     for i in r:
            #         print(f'  {i}')
            #         self.schedule_read_waiting_by_fd(i)
            # else:
            #     print(f'read ready: (none)')

            # if len(w) > 0:
            #     print(f'write ready:')
            #     for i in w:
            #         print(f'  {i}')
            #         self.schedule_write_waiting_by_fd(i)
            # else:
            #     print(f'write ready: (none)')

            if len(r) > 0:
                print(f'read ready:')
                for i in r:
                    print(f'  {i}')
            else:
                print(f'read ready: (none)')

            if len(w) > 0:
                print(f'write ready:')
                for i in w:
                    print(f'  {i}')
            else:
                print(f'write ready: (none)')

            consume(
                map(
                    #lambda fd: self.schedule(self.read_waiting.pop(fd)),
                    self.schedule_read_waiting_by_fd,
                    r,
                )
            )

            consume(
                map(
                    #lambda fd: self.schedule(self.write_waiting.pop(fd)),
                    self.schedule_write_waiting_by_fd,
                    w,
                )
            )

    def io_task(self):
        while True:
            if self.ready_queue.empty():
                print(f'ready queue is empty, waiting...')
                self.io_poll(None)
            else:
                self.io_poll(0)

            yield

    def schedule_read_waiting_by_fd(self, fd):
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        print(f'schedule_read_waiting_by_fd: {fd}')
        ready_task = self.read_waiting.pop(fd)
        self.schedule(ready_task)

    def schedule_write_waiting_by_fd(self, fd):
        if not isinstance(fd, int):
            raise TypeError(f'fd must be of type int, not {type(fd)}')
        print(f'schedule_write_waiting_by_fd: {fd}')
        ready_task = self.write_waiting.pop(fd)
        self.schedule(ready_task)

    def schedule(self, task):
        print(f'scheduling task {str(task)}')
        self.ready_queue.put(task)

    def run(self):
        self.new_task('Scheduler.io_task', self.io_task())
        print(f'running scheduler')
        while self.task_map:
            sleep(1.0)
            print(f'getting task')
            task = self.ready_queue.get()
            print(f'got task: {str(task)}')

            try:
                print(f'running task {str(task)}')
                result = task.run()
                if isinstance(result, ISystemCall):
                    print(f'got system call')
                    result.set_associated_task_and_scheduler(
                        task, scheduler=self)
                    result.handle()
                    continue
                print(f'not a system call: {result}')
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)





