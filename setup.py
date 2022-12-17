import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'construct<=2.10.0',
    'numba<=0.56.3']

setuptools.setup(
    name='live_trading_indicators',
    version='0.5.3',
    author="Aleksandr Kuznetsov",
    author_email="hal@hal9000.cc",
    description='A package for obtaining quotation data from various online and offline sources and calculating the values of'
                ' technical indicators based on these quotations.',

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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Office/Business :: Financial :: Investment"
    ],
    install_requires=requirements,
    extra_requires=['ccxt<=2.2.92', 'pandas<=1.5.0'],
    python_requires='>=3.7',
)
