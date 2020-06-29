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
    install_requires=[
        "requests~=2.23.0",
        "lxml~=4.5.0",
        "beautifulsoup4~=4.8.2",
        "PyYAML~=5.3.1",
    ],
    license="GNU GPL 3.0",
)
