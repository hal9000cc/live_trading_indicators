import setuptools
from src.live_trading_indicators import __version__ as version

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'construct<=2.10.70',
    'numba<=0.60.0',
    'lz4<=4.4.3']

setuptools.setup(
    name='live_trading_indicators',
    version=version,
    author="Aleksandr Kuznetsov",
    author_email="hal@hal9000.cc",
    description=
    "A package for obtaining quotation data from various sources and saving them to a database. "
    "Quotes can be quickly extracted and used for calculations and forecasts. "
    "It is possible to receive and process data in real time. "
    "There are a significant number of ready-to-use indicators. "
    "The integrity of the data stored in the database is carefully monitored.",

    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/hal9000cc/live_trading_indicators',

    packages=setuptools.find_packages(where='src'),
    package_dir={
        'live_trading_indicators': './src/live_trading_indicators',
        'datasources': './datasources'
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Office/Business :: Financial :: Investment"
    ],
    install_requires=requirements,
    extra_requires=['ccxt<=4.4.52', 'pandas<=2.2.3', 'matplotlib<=3.9.4'],
    python_requires='>=3.9',
)
