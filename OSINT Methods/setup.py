from setuptools import setup, find_packages

setup(
    name='automated_osint',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'python-whois',
        'shodan',
        'pandas',
        'phonenumbers',
        'timezonefinder',
        'geopy',
        'pycountry',
        'iso3166',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'automated_osint=automated_osint:main'
        ]
    },
    author='Foomey',
    description='An automated OSINT tool for website analysis.',
    url='https://github.com/f00Vmey',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
