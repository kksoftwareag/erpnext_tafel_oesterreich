from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in erpnext_tafel_oesterreich/__init__.py
from erpnext_tafel_oesterreich import __version__ as version

setup(
    name="erpnext_tafel_oesterreich",
    version=version,
    description="Frappe App for Tafel Oesterreich",
    author="K&K Software AG",
    author_email="teamx@kk-software.de",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
