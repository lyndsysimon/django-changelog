import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-changelog',
    version='0.0',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3 License',
    description='Easy change logging for Django models',
    long_description=README,
    url='https://www.github.com/lyndsysion/django-changelog/',
    author='Lyndsy Simon',
    author_email='lyndsy@lyndsysimon.com',
    test_suite="runtests.runtests",
    install_requires=[
        'psycopg2>=2.6',
        'Django>=1.9',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
