import json
from datetime import date, datetime
from hashlib import sha1, sha256
from pprint import pprint
from typing import List, Optional

from pydantic import BaseModel


class Task(BaseModel):
    name: str
    desc: str
    cat: Optional[str] = None
    deadline: Optional[date] = None


class Task_List(BaseModel):
    todos: List[Task]


def order(tasks: Task_List):
    task_list = tasks.todos

    # get cats and order them
    cat_tasks = [t for t in task_list if t.cat]
    cat_tasks.sort(key=lambda x: (x.cat, x.deadline))

    non_cat_tasks = [t for t in task_list if not t.cat]
    non_cat_tasks.sort(key=lambda x: (x.deadline is None, x.deadline))

    return Task_List(todos=cat_tasks + non_cat_tasks)


def hash_dict(tasks: Task_List):

    ordered_tasks = order(tasks=tasks)

    no_cat = "_"

    task_dict = {}
    for task in ordered_tasks.todos:
        if task.cat:
            if task.cat not in task_dict.keys():
                task_dict[task.cat] = {}

            task_dict[task.cat][to_hash(task=task)] = task.dict()

        else:
            if no_cat not in task_dict.keys():
                task_dict[no_cat] = {} 
            
            task_dict[no_cat][to_hash(task=task)] = task.dict()

    pprint(task_dict)

    return task_dict


def to_hash(task: Task):

    short_digest = sha256(json.dumps(
        task.__dict__, sort_keys=True, default=str).encode('utf-8')).hexdigest()[:10]

    return short_digest


def to_console(tasks : Task_List):

    task_hash_dict = hash_dict(tasks)

    for key in task_hash_dict.keys():

        print(f'Cat {key}')

        for task_hash in task_hash_dict[key]:
            print(f'\t{task_hash}')



if __name__ == "__main__":
    tasks = []
    tasks.append(Task(name="Task 1", desc="Test Task"))
    tasks.append(Task(name="Task 2", desc="test 2", deadline='2019-01-01'))
    tasks.append(Task(name="Task 3", desc="test 2", deadline='2019-01-02'))

    tasks.append(Task(name="Task 4", desc="test 2",
                      deadline='2019-01-01', cat="1"))
    tasks.append(Task(name="Task 5", desc="test 2",
                      deadline='2019-01-02', cat="1"))

    tasks.append(Task(name="Task 6", desc="test 2",
                      deadline='2019-06-12', cat="2"))
    tasks.append(Task(name="Task 7", desc="test 2",
                      deadline='2019-07-12', cat="2"))

    t = Task_List(todos=tasks)

    hash_dict(t)

    to_console(t)
