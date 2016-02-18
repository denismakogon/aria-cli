# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Handles 'aria commands'
"""

import json
import shutil
import os


from aria_processor import virtualenv_processor
from aria_processor import blueprint_processor

from aria_cli.commands import init as aria

from aria_core import blueprints
from aria_core import exceptions
from aria_core import utils
from aria_core import logger
from aria_core import workflows
from aria_core.dependencies import futures

_STORAGE_DIR_NAME = 'local-storage'
LOG = logger.get_logger('aria_cli.cli.main')


def validate(blueprint_path=None):
    return blueprints.validate(blueprint_path)


def init(blueprint_id,
         blueprint_path,
         inputs,
         install_plugins_):
    if os.path.isdir(_storage_dir(blueprint_id)):
        shutil.rmtree(_storage_dir(blueprint_id))

    if not utils.is_initialized():
        aria.init(reset_config=False, skip_logging=True)
    try:
        virtualenv_processor.initialize_blueprint(
            blueprint_path=blueprint_path,
            name=blueprint_id,
            inputs=inputs,
            storage=_storage(blueprint_id),
            install_plugins=install_plugins_,
            resolver=utils.get_import_resolver()
        )
    except ImportError as e:
        e.possible_solutions = [
            "Run 'aria init --install-plugins -p {0} -b {1}'"
            .format(blueprint_path,
                    blueprint_id),
            "Run 'aria install-plugins -p {0}'"
            .format(blueprint_path)
        ]
        raise e

    LOG.info(
        "Initiated {0}\nIf you make changes to the "
        "blueprint, "
        "Run 'aria init -p {0}' "
        "again to apply them"
        .format(blueprint_path))


def execute(blueprint_id,
            workflow_id,
            parameters,
            allow_custom_parameters,
            task_retries,
            task_retry_interval,
            task_thread_pool_size):
    parameters = utils.inputs_to_dict(parameters, 'parameters')
    result = workflows.generic_execute(
        workflow_id=workflow_id,
        parameters=parameters,
        allow_custom_parameters=allow_custom_parameters,
        task_retries=task_retries,
        task_retry_interval=task_retry_interval,
        task_thread_pool_size=task_thread_pool_size,
        environment=_load_env(blueprint_id))
    if result:
        LOG.info(json.dumps(result,
                            sort_keys=True,
                            indent=2))


def outputs(blueprint_id):
    env = _load_env(blueprint_id)
    _outputs = json.dumps(env.outputs() or {},
                          sort_keys=True, indent=2)
    LOG.info(_outputs)


def instances(blueprint_id, node_id):
    env = _load_env(blueprint_id)
    node_instances = env.storage.get_node_instances()
    if node_id:
        node_instances = [instance for instance in node_instances
                          if instance.node_id == node_id]
        if not node_instances:
            raise exceptions.AriaError('No node with id: {0}'
                                       .format(node_id))
    LOG.info(
        json.dumps(node_instances,
                   sort_keys=True,
                   indent=2))


def install_plugins(blueprint_path):
    virtualenv_processor.install_blueprint_plugins(
        blueprint_path=blueprint_path)


def create_requirements(blueprint_path, output):
    if output and os.path.exists(output):
        raise exceptions.AriaError('output path already exists : {0}'
                                   .format(output))

    requirements = blueprint_processor.create_requirements(
        blueprint_path=blueprint_path
    )

    if output:
        utils.dump_to_file(requirements, output)
        LOG.info(
            'Requirements created successfully --> {0}'
            .format(output))
    else:
        for requirement in requirements:
            print(requirement)
            LOG.info(requirement)


def _storage_dir(blueprint_id):
    return os.path.join(utils.get_cwd(),
                        _STORAGE_DIR_NAME,
                        blueprint_id)


def _storage(blueprint_id):
    return futures.aria_local.FileStorage(
        storage_dir=_storage_dir(blueprint_id))


def _load_env(blueprint_id):
    if not os.path.isdir(_storage_dir(blueprint_id)):
        error = exceptions.AriaError(
            '{0} has not been initialized with a blueprint.'
            .format(utils.get_cwd()))
        error.possible_solutions = [
            ("Run 'aria init -b [blueprint-id] "
             "-p [path-to-blueprint]' in this directory")
        ]
        raise error
    return futures.aria_local.load_env(name=blueprint_id,
                                       storage=_storage(blueprint_id))
