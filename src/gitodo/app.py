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


@app.command("add",help="Add a task to the list")
def add_task(
    name: str = typer.Argument("name"),
    desc: str = typer.Argument("desc"),
    cat: Optional[str] = typer.Option(None,"--cat", "-c"),
    deadline: Optional[str] = typer.Option(None,"--deadline","-d")
):
    """ Add a task 

        name : Name of the task.

        desc : Description what has to be done 

        cat (Optional) : A category. Used for grouping.

        deadline (Optional) : A duedate. Use the iso format.
    """
    command_args = {k:v for (k,v) in locals().items() if v is not None}
    if command_args == {"name":"name","desc":"desc"}:
        typer.echo("Default arguments, no task was created")
    else:
        with Tasks.from_file() as tasks:
            tasks.add_task(Task(**command_args))
        typer.echo("Added task ")

@app.command("finish")
def finish_task(
    task_hash : Optional[str] = typer.Option(None,"--hash","-h"),
    task_name : Optional[str] = typer.Option(None,"--name","-n"),
):
    """Finish a task and remove it from the list

        hash : part of task hash
        name : name of task
    """
    command_args = {k:v for (k,v) in locals().items() if v is not None} 
    with Tasks.from_file() as tasks:
        tasks.finish_task(**command_args)

@app.command("log")
def list_all_tasks():
    Tasks.from_file().print()


if __name__ == "__main__":
    app()
