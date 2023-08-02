from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in rc_swagger/__init__.py
from rc_swagger import __version__ as version

setup(
	name="rc_swagger",
	version=version,
	description="API Endpoint documentation of ERPNext endpoints using SWAGGER",
	author="RE-CA",
	author_email="mato.bodnar@re-ca.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
