from setuptools import setup
from setuptools import find_packages

setup(
    name='acquisition',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "inject_file = acquisition.inject_file:main",
            "reinject_step = acquisition.reinject_step:main",
        ]
    }
)
