import os
from setuptools import setup

import dirty_models_sphinx

setup(
    name='dirty-models-sphinx',
    url='https://github.com/alfred82santa/dirty-models-sphinx',
    author='alfred82santa',
    author_email='alfred82santa@gmail.com',
    license='GPLv2',
    version=dirty_models_sphinx.__version__,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta'],
    packages=['dirty_models_sphinx'],
    install_requires=['dirty-models', 'sphinx'],
    include_package_data=False,
    description='Sphinx extension for dirty models',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    zip_safe=True,
)
