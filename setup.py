from distutils.core import setup
import setuptools

setup(
    name='DesktopLedDisplay',
    version='0.1dev',
	author="Caleb Stamper",
    packages=setuptools.find_packages(),
    license=open('LICENSE').read(),
    long_description=open('README').read(),
)