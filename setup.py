
from setuptools import setup

setup(
    name="craigslist_notify",
    version="0.1.0",
    description="Python bot for listing alerts",
    author="rwev",
    author_email="rwev@rwev.dev",
    url="https://gitlab.com/rwev/craigslist_notify",
    packages=["craigslist_notify"],
    include_package_data=True,
    entry_points={"console_scripts": "craigslist_notify=craigslist_notify.main:main"},
    install_requires=[],
    license="GNU GPL 3.0",
)