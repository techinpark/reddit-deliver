"""
Setup script for reddit-deliver package.
"""

from setuptools import setup, find_packages

setup(
    name="reddit-deliver",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "praw>=7.7.0",
        "deepl>=1.16.0",
        "google-genai>=1.0.0",
        "requests>=2.31.0",
        "sqlalchemy>=2.0.0",
        "apscheduler>=3.10.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "reddit-deliver=cli.main:main",
        ],
    },
    python_requires=">=3.11",
)
