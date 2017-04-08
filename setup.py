from setuptools import setup, find_packages

setup(
    name='compapp',
    version='0.1.0.dev1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Takafumi Arakaki',
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/compapp',
    license='BSD-2-Clause',  # SPDX short identifier
    description='A framework for simulations and data analysis',
    long_description=open('README.rst').read(),
    keywords='numerical simulation, research',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        # 'SOME_PACKAGE',
    ],
    entry_points={
        'console_scripts': ['capp = compapp.cli:main'],
    },
)
