from setuptools import setup


setup(
    name='manly',
    author='Carl Bordum Hansen',
    license='MIT',
    url='https://github.com/Zaab1t/manly',
    py_modules=['manly'],
    entry_points={
        'console_scripts': ['manly=manly:main'],
    },
)
