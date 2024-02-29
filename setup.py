from setuptools import setup, find_packages

setup(
    name='dawnet-cli',
    version='0.0.1',
    author='Steve Hiehn',
    author_email='stevehiehn@gmail.com',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'click',
        'questionary',
        # other dependencies
    ],
    entry_points={
        'console_scripts': [
            'dawnet=dawnet_cli.cli:main',
        ],
    },
    # Other metadata
    description='A python CLI used to manage DAWnet remotes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
