
# from typing import Coroutine


class Task():
    task_id = 0

    def next_task_id() -> int:
        Task.task_id += 1
        return Task.task_id

    def __init__(self, name:str, target) -> None:
        if not isinstance(name, str):
            raise TypeError(f'name must be of type str, not {type(name)}')
        # if not isinstance(target, Coroutine):
        #     raise TypeError(f'name must be of type Coroutine, not {type(target)}')
        task_id = Task.next_task_id()
        print(f'created new task with id {task_id}, target={target.__name__}')

        self.task_id = task_id
        self.name = name
        self.target = target
        self.sendval = None

    def run(self):
        return self.target.send(self.sendval)

    def get_task_id(self) -> int:
        return self.task_id

    def __str__(self) -> str:
        if hasattr(self.target, '__name__'):
            return f'{self.task_id}:{self.name} -> {self.target.__name__}'
        else:
            return f'{self.task_id}:{self.name} -> <UNNAMED>'
