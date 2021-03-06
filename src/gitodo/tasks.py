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

    def to_hashed_tasks(self):
        return Hashed_Tasks(tasks = self)

    def _hash_dict(self) -> Dict[str,Dict[str,Dict]]:
        """Create hash for every task that functions as key

        Args:
            tasks : listed tasks

        Returns:
            a dict with cat as first key and hash as task key
        """
        ordered_tasks = self.order()
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

    def to_console(self) -> None:
        """Generate a colorcoded terminal output of the tasks

        Args:
            tasks : the list of tasks
        """
        task_hash_dict = self._hash_dict()
        if task_hash_dict == {}:
            raise ValueError("No task present yet")
        longest_cat = max(list(map(len,task_hash_dict.keys())))
        longest_name = max([len(task.name) for task in self.todos])


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

    def order(self) -> "Task_List":
        """Order the task list by cat and due date

        Args:
            tasks : Task_List object

        Returns:
            ordere Task_List object
        """
        task_list = self.todos

        # get cats and order them
        cat_tasks = [t for t in task_list if t.cat]
        cat_tasks.sort(key=lambda x: (x.cat, x.deadline is None))

        non_cat_tasks = [t for t in task_list if not t.cat]
        non_cat_tasks.sort(key=lambda x: (x.deadline is None, x.deadline))

        return Task_List(todos=cat_tasks + non_cat_tasks)


TASKS_PATH = Path(".gitodo")

class Tasks:
    def __init__(self, path : Path = TASKS_PATH, tasks : Task_List = Task_List(todos=[])) -> None:
        """A object to handle all tasks

        Args:
            path : path to save and load from
            tasks : Task_List object
        """
        self.path = Path(path)
        self._task_list  = tasks
        self._hashed_tasks_dict = self._task_list.to_hashed_tasks()


    @classmethod
    def from_file(cls, path : Path = TASKS_PATH) -> "Tasks":
        """Load tasks from a json file

        Returns:
            Tasks object
        """
        with open(path,'r') as tasks_json_file:
            tasks_dict = json.load(tasks_json_file)

        task_list = list()
        for (_,cat_tasks) in tasks_dict.items():
            for task in cat_tasks.values():
                task_list.append(Task(**task))

        return cls(
            path = path,
            tasks = Task_List(todos = task_list)
            )

    def to_list(self) -> List[Task]:
        return self._task_list.todos

    def print(self) -> None:
        """Generate terminal output
        """
        try:
            self._task_list.to_console()
        except ValueError as ve:
            print(str(ve))

    def add_task(self, task : Task) -> None:
        """Add a task to the list

        Args:
            task : Task Object
        """
        self._task_list.todos.append(task)
        self._hashed_tasks_dict = self._task_list.to_hashed_tasks()

    def find_task(self, task_hash : str = "", task_name : str = "") -> List[Task]:
        """Find a task by name or part of the hash. Returns a list with all mathing tasks

        Args:
            task_hash : Hast of the task. Defaults to "".
            task_name : Name of the task. Defaults to "".

        Returns:
            listed Task objects
        """
        try:        
            if task_hash != "":
                return find_task_for_hash(self._hashed_tasks_dict, short_hash= task_hash)

            if task_name != "":
                return find_task_for_name(self._task_list, name = task_name) 

        except KeyError as ke:
            print(str(ke))

    def finish_task(self, task_hash : str = "", task_name : str = "") -> None:
        """Finish a task. It will be removed from the list.

        Args:
            task_hash : Hash of the task object. Defaults to "".
            task_name : Name of the task. Defaults to "".
        """
        matched_tasks : Task_List = self.find_task(
            task_hash = task_hash,
            task_name = task_name
        )
        if len(matched_tasks.todos) != 1:
            print("No specific task could be found")
        else:
            self._hashed_tasks_dict._pop(task=matched_tasks.todos[0])
            print(f"Task {matched_tasks.todos[0]} removed from list")
            self._task_list = self._hashed_tasks_dict.to_task_list()

    def save(self, path : Path = None) -> None:
        """Export the tasks to a json file

        Args:
            path : destination path. Defaults to path set in init.
        """
        if path is None:
            path = self.path

        Path("".join(path.parts[:-1])).mkdir(parents=True, exist_ok=True)                

        with open(path,"w") as json_file:
            json.dump(
                obj=self._hashed_tasks_dict.hashed,
                default=self._hashed_tasks_dict._hashed_task_serializer,
                fp=json_file,
                ensure_ascii=True,
                indent=2
            )

    def __enter__(self) -> "Tasks":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.save()

class Hashed_Tasks:
    def __init__(self, tasks : Task_List) -> List[Task]:
        """Hash representation of the tasks

        Args:
            tasks : a Task_List object
        """
        self._hashed_tasks = tasks._hash_dict()

    def _pop(self, task : Task) -> Task:
        """Pop tasks from the dict

        Args:
            task : task that should be removed 

        Returns:
            poped task
        """
        matches = list()
        for (cat_key,cat_task) in self._hashed_tasks.items():
            for (task_hash,task_value) in cat_task.items():
                if task == task_value:
                    matches.append((cat_key,task_hash))

        for (cat,task_hash) in matches:
            return self._hashed_tasks[cat].pop(task_hash)

    @property
    def hashed(self):
        """Returns the hash dict

        Returns:
            Hashed tasks
        """
        return self._hashed_tasks

    def to_task_list(self) -> Task_List:
        """Convert the hash list to a Task_List

        Returns:
            Task_List object
        """
        task_list = list()
        for cat_tasks in self._hashed_tasks.values():
            for task in cat_tasks.values():
                task_list.append(Task(**task))

        return Task_List(todos=task_list)

    def _hashed_task_serializer(self,o):
        """Internal function to seriialize the object, specific the datetime object

        Args:
            o : object

        Returns:
            datetime in isoformat
        """
        if isinstance(o, (date, datetime)):
            return o.isoformat()

def find_task_for_hash(hashed_tasks : Hashed_Tasks, short_hash : str) -> Task_List:
    """Find tasks mathing a hash or part of a hash

    Args:
        hashed_tasks : hashed tasks
        short_hash : string with hash or part of the hash

    Raises:
        KeyError: if a tasked could not be found

    Returns:
        
    """
    task_matches = list()
    # hashed_tasks = hash_dict(tasks)
    for hashed_task_cat in hashed_tasks.hashed.keys():
        cat_x_tasks = hashed_tasks.hashed[hashed_task_cat]
        for hashed_task_key in cat_x_tasks.keys(): 
            if short_hash in hashed_task_key:
                task_matches.append(Task(**cat_x_tasks[hashed_task_key]))

    if len(task_matches) > 0:
        return Task_List(todos=task_matches)
    else:
        raise KeyError("Task hash not found")


def find_task_for_name(tasks : Task_List, name : str) -> Task_List:
    task_matches = list()    
    for task in tasks.todos:
        # TODO : Use fuzzy matching
        if task.name == name:
            task_matches.append(task)

    if len(task_matches) > 0:
        return Task_List(todos=task_matches)
    else:
        raise KeyError("Task name not found")



