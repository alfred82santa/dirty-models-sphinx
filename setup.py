import ast

import os
from setuptools import setup

path = os.path.join(os.path.dirname(__file__), 'dirty_models_sphinx', '__init__.py')

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

setup(
    name='dirty-models-sphinx',
    url='https://github.com/alfred82santa/dirty-models-sphinx',
    author='alfred82santa',
    author_email='alfred82santa@gmail.com',
    license='GPLv2',
    version=version,
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
