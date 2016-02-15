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

from setuptools import setup


setup(
    name='aria-tosca',
    version='0.5',
    author='Aria-TOSCA',
    author_email='Aria-TOSCA@aria.io',
    packages=['aria_cli',
              'aria_cli.commands',
              'aria_cli.config'],
    package_data={
        'aria_cli': [
            'VERSION',
            'resources/config.yaml',
        ],
    },
    license='LICENSE',
    description='ARIA CLI',
    entry_points={
        'console_scripts': [
            'aria = aria_cli.cli:main',
            'activate_aria_bash_completion = aria_cli.activate_bash_completion:main'  # NOQA
        ]
    },
    install_requires=[
        'aria-plugins-common==0.3',
        'aria-dsl-parser==0.3',
        'pyyaml==3.10',
        'argcomplete==0.7.1',
        'jinja2==2.7.2',
    ]
)
