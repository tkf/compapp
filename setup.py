from distutils.core import setup

import compapp

setup(
    name='compapp',
    version=compapp.__version__,
    packages=['compapp'],
    author=compapp.__author__,
    author_email='aka.tkf@gmail.com',
    # url='https://github.com/tkf/compapp',
    license=compapp.__license__,
    # description='compapp - THIS DOES WHAT',
    long_description=compapp.__doc__,
    # keywords='KEYWORD, KEYWORD, KEYWORD',
    classifiers=[
        "Development Status :: 3 - Alpha",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        # 'SOME_PACKAGE',
    ],
)
