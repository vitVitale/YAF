from setuptools import find_packages, setup

setup(
    name='yaf_lib',
    packages=find_packages(include=[
        'yaf',
        'yaf.app',
        'yaf.data',
        'yaf.data.parsers',
        'yaf.fabric',
        'yaf.fabric.clientTypes',
        'yaf.steps',
        'yaf.utils'
    ]),
    version='1.8.7',
    description='YAF (Yet Another Framework) library for backend automated testing with YAML contract usage',
    author='Vasiliuk Vitalii',
    author_email="vitvasilyuk@gmail.com",
    license='----',
    include_package_data=True,
    install_requires=[
        x.strip() for x in open('requirements.txt', 'r').readlines()
    ],
    setup_requires=[],
    tests_require=['pytest==6.2.5'],
    test_suite='tests'
)
