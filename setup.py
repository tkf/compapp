from setuptools import setup, find_packages

setup(
    name='compapp',
    version='0.0.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Takafumi Arakaki',
    author_email='aka.tkf@gmail.com',
    # url='https://github.com/tkf/compapp',
    # license=,
    # description='compapp - THIS DOES WHAT',
    long_description=open("README.rst").read(),
    # keywords='KEYWORD, KEYWORD, KEYWORD',
    classifiers=[
        "Development Status :: 3 - Alpha",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        # 'SOME_PACKAGE',
    ],
    entry_points={
        'console_scripts': ['capp = compapp.cli:main'],
    },
)
