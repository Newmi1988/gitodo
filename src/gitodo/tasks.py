import json
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel
from termcolor import colored, cprint


class Task(BaseModel):
    name: str
    desc: str
    cat: Optional[str] = None
    deadline: Optional[date] = None

    def to_hash(self):
        short_digest = sha256(
            json.dumps(
                self.dict(), 
                sort_keys=True, 
                default=str
                ).encode('utf-8')
            ).hexdigest()[:10]

        return short_digest


class Task_List(BaseModel):
    todos: List[Task]


class Tasks:
    def __init__(self, path : Path, tasks : Task_List) -> None:
        self.path = path
        self._task_list  = tasks
        self.hashed_tasks_dict  = Hashed_Tasks(
            tasks=tasks
            )

    @classmethod
    def from_file(cls, path : Path) -> "Tasks":
        return cls(path)

    @property
    def list(self):
        return self._task_list

    def print(self):
        to_console(self._task_list)

    def add_task(self, task : Task):
        self._task_list.todos.append(task)

    def find_task(self, task_hash : str = "", task_name : str = ""):
        try:        
            if task_hash != "":
                return find_task_for_hash(self.hashed_tasks_dict, short_hash= task_hash)

            if task_name != "":
                return find_task_for_name(self._task_list, name = task_name) 

        except KeyError as ke:
            print(str(ke))

    def finish_task(self, task_hash : str = "", task_name : str = ""):
        matched_tasks = self.find_task(
            task_hash = task_hash,
            task_name = task_name
        )
        if len(matched_tasks) != 1:
            print("No specific task could be found")
        else:
            self.hashed_tasks_dict.pop(task=matched_tasks[0])
            print(f"Task {matched_tasks[0]} removed from list")
            self._task_list = self.hashed_tasks_dict.task_list()



class Hashed_Tasks:
    def __init__(self, tasks : Task_List) -> None:
        self._hashed_tasks = hash_dict(tasks = tasks)

    def pop(self, task : Task) -> "Hashed_Tasks":
        matches = list()
        for (cat_key,cat_task) in self._hashed_tasks.items():
            for (task_hash,task_value) in cat_task.items():
                if task == task_value:
                    print("found")
                    matches.append((cat_key,task_hash))

        for (cat,task_hash) in matches:
            self._hashed_tasks[cat].pop(task_hash)

    @property
    def hashed(self):
        return self._hashed_tasks

    def task_list(self):
        task_list = list()
        for cat_tasks in self._hashed_tasks.values():
            for task in cat_tasks.values():
                task_list.append(Task(**task))

        return Task_List(todos=task_list)


def hash_dict(tasks: Task_List):
    ordered_tasks = order(tasks=tasks)
    no_cat = "_"
    task_dict = {}
    for task in ordered_tasks.todos:
        if task.cat:
            if task.cat not in task_dict.keys():
                task_dict[task.cat] = {}

            task_dict[task.cat][task.to_hash()] = task.dict()

        else:
            if no_cat not in task_dict.keys():
                task_dict[no_cat] = {} 
            
            task_dict[no_cat][task.to_hash()] = task.dict()

    return task_dict


def order(tasks: Task_List):
    task_list = tasks.todos

    # get cats and order them
    cat_tasks = [t for t in task_list if t.cat]
    cat_tasks.sort(key=lambda x: (x.cat, x.deadline))

    non_cat_tasks = [t for t in task_list if not t.cat]
    non_cat_tasks.sort(key=lambda x: (x.deadline is None, x.deadline))

    return Task_List(todos=cat_tasks + non_cat_tasks)


def to_console(tasks : Task_List):
    task_hash_dict = hash_dict(tasks)
    longest_cat = max(list(map(len,task_hash_dict.keys())))
    longest_name = max([len(task.name) for task in tasks.todos])


    for key in task_hash_dict.keys():

        category = key

        for task_hash in task_hash_dict[key]:
            task = Task(**task_hash_dict[category][task_hash])

            task_hash_str = f'{task_hash}'
            date = f'-> [{task.deadline.strftime("%d-%d-%Y")}]' if task.deadline else ' '*15
            whitespace_cat = ' '*(longest_cat-len(category))
            whitespace_name = ' '*(longest_name-len(task.name))

            print(
                colored(task_hash_str,'yellow'),
                colored(f'{date}','red'),
                colored(f'({category})','green'),
                colored(f'{whitespace_cat}{task.name}{whitespace_name}','cyan'),
                f': {task.desc}'
            )


def find_task_for_hash(hashed_tasks : Hashed_Tasks, short_hash : str):
    task_matches = list()
    # hashed_tasks = hash_dict(tasks)
    for hashed_task_cat in hashed_tasks.hashed.keys():
        cat_x_tasks = hashed_tasks.hashed[hashed_task_cat]
        for hashed_task_key in cat_x_tasks.keys(): 
            if short_hash in hashed_task_key:
                task_matches.append(Task(**cat_x_tasks[hashed_task_key]))

    if len(task_matches) > 0:
        return task_matches
    else:
        raise KeyError("Task hash not found")


def find_task_for_name(tasks : Task_List, name : str):
    task_matches = list()    
    for task in tasks.todos:
        # TODO : Use fuzzy matching
        if task.name == name:
            task_matches.append(task)

    if len(task_matches) > 0:
        return task_matches
    else:
        raise KeyError("Task name not found")


if __name__ == "__main__":
    tasks = []
    tasks.append(Task(name="gitodo", desc="Test Task"))
    tasks.append(Task(name="a", desc="Continue this program", deadline='2019-01-01'))
    tasks.append(Task(name="Task 3", desc="test 2", deadline='2019-01-02'))

    tasks.append(Task(name="dinner", desc="make dinner",
                      deadline='2019-01-01', cat="gitodo"))
    tasks.append(Task(name="Task 5", desc="test 2",
                      deadline='2019-01-02', cat="gitodo"))

    tasks.append(Task(name="Task 6", desc="test 2",
                      deadline='2019-12-01', cat="2"))
    tasks.append(Task(name="Task 7", desc="test 2",
                      deadline='2019-12-02', cat="2"))

    t = Task_List(todos=tasks)

    # hash_dict(t)

    # to_console(t)

    Test = Tasks(path = Path("."), tasks= t)
    Test.print()

    # TODO : Fix adding task
    Test.add_task(Task(
        name = "Blub", 
        desc ="Make blub", 
        deadline="2021-12-31",
        cat = "Test")
        )

    # print(Test.find_task(task_hash="421"))
    # print(Test.find_task(task_name="Task 6"))

    Test.finish_task(task_hash="421")

    Test.print()
