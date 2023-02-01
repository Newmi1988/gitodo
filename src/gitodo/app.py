#!/usr/bin/python

from typing import Optional

import typer

from gitodo.tasks import TASKS_PATH, Task, Tasks

app = typer.Typer()


@app.command("init")
def init_task_file(path: str = typer.Argument(str(TASKS_PATH))):
    tasks = Tasks(path)
    tasks.save()

    typer.echo("Created new tasks file")


@app.command("add", help="Add a task to the list")
def add_task(
    name: str = typer.Argument("name"),
    desc: str = typer.Argument("desc"),
    cat: Optional[str] = typer.Option(None, "--cat", "-c"),
    deadline: Optional[str] = typer.Option(None, "--deadline", "-d"),
):
    """Add a task

    name : Name of the task.

    desc : Description what has to be done

    cat (Optional) : A category. Used for grouping.

    deadline (Optional) : A duedate. Use the iso format.
    """
    command_args = {k: v for (k, v) in locals().items() if v is not None}
    if command_args == {"name": "name", "desc": "desc"}:
        typer.echo("Default arguments, no task was created")
    else:
        with Tasks.from_file() as tasks:
            tasks.add_task(Task(**command_args))
        typer.echo("Added task ")


@app.command("get", help="Get specific task")
def get_task(
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    partial_hash: Optional[str] = typer.Option(None, "--partial-hash", "-h"),
):
    """Filter the task by name or partial hash

    name : Name of the task.
    partial_hash: Hash or part of hash to filter by

    """
    if not name and not partial_hash:
        typer.echo("You have to supply a name and/or a partial hash")
    else:
        try:
            task = Tasks.from_file().find_task(task_hash=partial_hash, task_name=name)
            if task:
                task.to_console()

        except ValueError as ve:
            print(ve)


@app.command("finish")
def finish_task(
    task_hash: Optional[str] = typer.Option(None, "--hash", "-h"),
    task_name: Optional[str] = typer.Option(None, "--name", "-n"),
):
    """Finish a task and remove it from the list

    hash : part of task hash
    name : name of task
    """
    command_args = {k: v for (k, v) in locals().items() if v is not None}
    with Tasks.from_file() as tasks:
        tasks.finish_task(**command_args)


@app.command("list")
def list_all_tasks(
    cat: Optional[str] = typer.Option(None, "--cat", "-c"),
):
    Tasks.from_file().print(cat)


if __name__ == "__main__":
    app()
