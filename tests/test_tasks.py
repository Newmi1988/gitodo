import datetime
import os
import random
import re
import string
from pathlib import Path

import pytest
from termcolor import colored

from gitodo.tasks import TASKS_PATH, Task, Task_List, Tasks


@pytest.fixture
def identity_task():
    return Task(**{
        "name": "name",
        "desc": "desc",
        "cat": "cat"
    })


def random_str():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))


def random_task_cat_x():
    return {
        "name": random_str(),
        "desc": random_str(),
        "cat": "Cat x",
        "deadline": "2021-01-01"
    }


@pytest.fixture
def gen_random_task_cat_x():
    return random_task_cat_x


def random_task_cat_y():
    return {
        "name": random_str(),
        "desc": random_str(),
        "cat": "Cat y",
        "deadline": "2021-01-01"
    }


@pytest.fixture
def gen_random_task_cat_y():
    return random_task_cat_y


def random_task_no_cat():
    return {
        "name": random_str(),
        "desc": random_str(),
        "deadline": "2021-01-01"
    }


class Test_Task_Class:
    def test_name_desc_task(self):
        t = Task(name="name", desc="desc")

        assert t.dict() == {"name": "name", "desc": "desc",
                            "cat": None, "deadline": None}

    def test_task_with_deadline(self):
        t = Task(
            name="name",
            desc="desc",
            deadline="2021-01-01"
        )

        assert t.dict() == {
            "name": "name",
            "desc": "desc",
            "deadline": datetime.date.fromisoformat("2021-01-01"),
            "cat": None
        }

    def test_task_with_cat(self):
        t = Task(
            name="name",
            desc="desc",
            cat="cat"
        )

        assert t.dict() == {
            "name": "name",
            "desc": "desc",
            "deadline": None,
            "cat": "cat"
        }

    def test_task_with_cat_deadline(self):
        t = Task(
            name="name",
            desc="desc",
            cat="cat",
            deadline="2021-01-01"
        )

        assert t.dict() == {
            "name": "name",
            "desc": "desc",
            "deadline": datetime.date.fromisoformat("2021-01-01"),
            "cat": "cat"
        }

    def test_task_hash(self, gen_random_task_cat_x):

        t_hash = Task(**gen_random_task_cat_x()).to_hash()

        assert re.match(r"([a-fA-F\d]{10})", t_hash)


@pytest.fixture
def random_task_list():
    l = list()
    for _ in range(20):
        random_task_generator = random.choice(
            [random_task_cat_y, random_task_cat_x, random_task_no_cat])
        l.append(Task(**random_task_generator()))

    return Task_List(todos=l)


class Test_Task_List:

    def test_creation(self):

        l = list()
        for _ in range(10):
            l.append(Task(**random_task_cat_x()))

        tl = Task_List(todos=l)

        for i, j in zip(l, tl.todos):
            assert i == j

    def test_to_console(self,identity_task,capsys):
        t = Task_List(todos=[identity_task])
        t.to_console()
        out, err = capsys.readouterr()
        out = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', out)

        desired_string = f"{identity_task.to_hash()}                 ({identity_task.cat}) {identity_task.name} : {identity_task.desc}"
        assert out.replace("\n","") == desired_string

    def test_empty_print(self):
        t = Task_List(todos=[])
        with pytest.raises(ValueError):
            t.to_console()

    def test_hash_dict_conversion(self, random_task_list):

        t = random_task_list._hash_dict()

        for (cat, cat_tasks) in t.items():
            assert cat in ['Cat x', 'Cat y', '_']

            if cat == '_':
                cat = None

            for task_hash, task in cat_tasks.items():
                assert re.match(r"([a-fA-F\d]{10})", task_hash)
                assert task["cat"] == cat
                assert task_hash == Task(**task).to_hash()

    def test_order(self, random_task_list):

        ordered_list = random_task_list.order()

        ordered_cats = [
            task.cat for task in ordered_list.todos if task.cat is not None]
        ordered_cat_date = [
            task.deadline for task in ordered_list.todos if task.cat is not None]
        ordered_date_non_cat = [
            task.deadline for task in ordered_list.todos if task.cat is None]

        assert all(ordered_cats[i] <= ordered_cats[i+1]
                   for i in range(len(ordered_cats)-1))
        assert all(ordered_cat_date[i] <= ordered_cat_date[i+1]
                   for i in range(len(ordered_cat_date)-1))
        assert all(ordered_date_non_cat[i] <= ordered_date_non_cat[i+1]
                   for i in range(len(ordered_date_non_cat)-1))


@pytest.fixture
def empty_tasks():
    return Tasks(tasks=Task_List(todos=[]))


class Test_Tasks:
    def test_init(self, random_task_list):

        random_tasks = Tasks(tasks=random_task_list)
        assert random_tasks.path == TASKS_PATH
        assert random_tasks._task_list == random_task_list

    def test_from_file(self):

        t = Tasks.from_file(Path("./tests/.gitodo.test"))

        assert isinstance(t, Tasks)

    def test_add_task(self, empty_tasks):
        test_task = Task(**random_task_cat_y())
        empty_tasks.add_task(test_task)

        t = empty_tasks.to_list()

        t[0].cat == test_task.cat

    def test_find_task_by_name(self, empty_tasks, identity_task):

        empty_tasks.add_task(identity_task)

        found_task = empty_tasks.find_task(task_name = identity_task.name).todos

        assert found_task[0].name == identity_task.name
        assert found_task[0].desc == identity_task.desc
        assert found_task[0].cat == identity_task.cat

    def test_print(self,empty_tasks, identity_task, capsys):

        empty_tasks.print()
        out, err = capsys.readouterr()
        assert out.replace("\n","") == "No task present yet"      

    def test_finish_task(self,empty_tasks, identity_task):

        empty_tasks.add_task(identity_task)

        empty_tasks.finish_task(task_name = "name")

        assert len(empty_tasks.to_list()) == 0


    def test_find_task_by_hash(self, empty_tasks, identity_task,capsys):

        empty_tasks.add_task(identity_task)

        found_task = empty_tasks.find_task(task_hash = identity_task.to_hash()).todos

        assert found_task[0].name == identity_task.name
        assert found_task[0].desc == identity_task.desc
        assert found_task[0].cat == identity_task.cat


    def test_find_task_by_hash_wrong_hash(self, empty_tasks, identity_task,capsys):
        empty_tasks.add_task(identity_task)
        empty_tasks.find_task(task_hash = "abc")
        out, err = capsys.readouterr()
        assert out.replace("\n","").replace("'","") == "Task hash not found"

    def test_find_task_by_hash_wrong_name(self, empty_tasks, identity_task,capsys):
        empty_tasks.add_task(identity_task)
        empty_tasks.find_task(task_name = "abc")
        out, err = capsys.readouterr()
        assert out.replace("\n","").replace("'","") == "Task name not found"

    def test_save(self,random_task_list):
        t = Tasks(tasks = random_task_list)

        test_save = Path("./tests/.gitodo.delme")

        t.save(path = test_save)

        assert test_save.is_file()

        t_reload = Tasks.from_file(test_save)

        os.remove(test_save)

        t_hashes = [task.to_hash() for task in t.to_list()]
        t_reload_hashes = [task.to_hash() for task in t_reload.to_list()]

        assert len(t_hashes) == len(t_reload_hashes)
        assert len(set(t_hashes).intersection(set(t_reload_hashes))) == len(t_hashes)         
            

