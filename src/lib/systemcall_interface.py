
from .task import Task

from .scheduler_interface import IScheduler


class ISystemCall:

    def handle():
        pass

    def set_associated_task_and_scheduler(
        self,
        task: Task,
        scheduler: IScheduler,
    ) -> None:
        if not isinstance(task, Task):
            print(f'task must be of type Task, not {type(task)}')
        if not isinstance(scheduler, IScheduler):
            print(f'scheduler must be of type IScheduler, not {type(scheduler)}')
        self.task = task
        self.scheduler = scheduler

