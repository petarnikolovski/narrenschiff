import os

import click
import yaml

from narrenschiff.task import Task
from narrenschiff.task import TasksEngine
from narrenschiff.templating import Template


@click.command()
@click.option('--set-course', 'course', help='Path to your YAML course file.')
def deploy(course):
    """
    Turn tasks into actions.

    :param course: The path to ``course`` file. A file containing tasks
        specified in the YAML format. Tasks are ``executable`` pieces of
        configuration. Course is Jinja2 templated file (as are all the
        kubernetes manifest files)
    :type course: ``str``
    :return: Void
    :rtype: ``None``
    """
    template = Template(course)
    tasks = _import_course(course, template)

    template.render_all_files()

    engine = TasksEngine(tasks)
    engine.run()

    template.clear_templates()


def _import_course(course, template):
    """
    Recursively load all courses and return tasks
    """
    tasks_yaml = _import_current_tasks(course, template)

    tasks = []
    for task in tasks_yaml:
        follow_course = task.get('import_course')
        if follow_course:
            new_tasks = _import_course(follow_course, template)
            for new_task in new_tasks:
                tasks.append(new_task)
        else:
            tasks.append(Task(task, template))

    return tasks


def _import_current_tasks(course, template):
    """
    Render tasks
    """
    tasks_raw = template.render(os.path.basename(course))
    tasks_yaml = yaml.load(tasks_raw, Loader=yaml.FullLoader)
    return tasks_yaml
