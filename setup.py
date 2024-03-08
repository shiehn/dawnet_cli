from setuptools import setup, find_packages

setup(
    name="dawnet-cli",
    version="0.0.1",
    author="Steve Hiehn",
    author_email="stevehiehn@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click",
        "docker",
        "questionary",
        "urllib3",
        "requests",
        "appdirs",
        # other dependencies
    ],
    entry_points={
        "console_scripts": [
            "dawnet=dawnet_cli.cli:main",
        ],
    },
    # Other metadata
    description="A python CLI used to manage DAWnet remotes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
