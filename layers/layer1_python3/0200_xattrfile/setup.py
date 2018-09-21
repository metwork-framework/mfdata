from setuptools import setup
from setuptools import find_packages

setup(
    name='xattrfile',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "print_tags = xattrfile.print_tags:main",
            "get_tag = xattrfile.get_tag:main",
            "set_tag = xattrfile.set_tag:main"
        ]
    }
)
