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
            "switch_step = acquisition.switch_step:main",
            "archive_step = acquisition.archive_step:main",
            "copy_step = acquisition.copy_step:main",
            "move_step = acquisition.move_step:main",
            "fork_step = acquisition.fork_step:main",
            "delete_step = acquisition.delete_step:main",
            "ungzip_step = acquisition.ungzip_step:main",
            "unbzip2_step = acquisition.unbzip2_step:main",
        ]
    }
)
