from functools import partial
from inspect import getmembers, isfunction
from typing import Callable, Dict, List

from pandas import DataFrame

from linuxforhealth.csvtofhir.model.contract import Task
from linuxforhealth.csvtofhir.pipeline import tasks as pipeline_tasks
from linuxforhealth.csvtofhir.support import get_logger

logger = get_logger(__name__)


def load_tasks() -> Dict:
    """ "
    Loads a Dictionary containing Task functions.
    Key = Task/Function Name
    Value = Task/Function
    """
    task_map = {}

    for m in getmembers(pipeline_tasks, isfunction):
        task_name = m[0]
        task = m[1]

        if task_name.startswith("_") or task_name in ["parse"]:
            logger.warning(f"Skipping task {task_name}")
            continue

        task_map[task_name] = task
    return task_map


TASKS = load_tasks()


def parse(tasks: List[Task]) -> List[Callable]:
    """
    Parses a list of task definitions into a list of executable functions.
    Parameters are applied to the task as a partial function.

    :param tasks: List of tasks to parse
    :return: List of ready to use Callables
    """
    functions: List[Callable] = []

    for t in tasks:
        task: Callable = TASKS[t.name]
        params = t.params or {}
        if params:
            task = partial(task, **params)
        functions.append(task)

    return functions


def execute(tasks: List[Task], data_frame: DataFrame) -> DataFrame:
    """
    Executes tasks against a DataFrame, returning an updated DataFrame.

    :param data_frame: The input DataFrame
    :param tasks: List of Tasks to execute
    :return: the updated DataFrame
    """
    for t in parse(tasks):
        try:
            data_frame = t(data_frame=data_frame)
        except Exception as ex:
            logger.error(f"Error executing task {t} Exception = {ex}")
    return data_frame
