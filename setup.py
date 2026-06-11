from setuptools import find_packages, setup


setup(
    name="alarm-clock-cli",
    version="0.1.0",
    description="Clean architecture alarm clock CLI.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["typer>=0.12.0"],
    extras_require={"dev": ["pytest>=8.0.0"]},
    entry_points={"console_scripts": ["alarm=alarm_clock.main:main"]},
)
