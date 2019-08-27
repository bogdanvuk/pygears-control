from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(this_directory, 'README.rst'),
              encoding='utf-8') as f:
        return f.read()


setup(
    name='pygears-control',
    version='0.0.1',
    description='PyGears library for developping system control',
    long_description=readme(),
    url='https://www.pygears.org',
    # download_url = '',
    author='Bogdan Vukobratovic',
    author_email='bogdan.vukobratovic@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6.0',
    install_requires=['PySpice', 'scipy', 'matplotlib', 'control'],
    setup_requires=['PySpice', 'scipy', 'matplotlib', 'control'],
    package_data={'': ['*.j2', '*.sv']},
    include_package_data=True,
    keywords=
    'PyGears functional hardware design Python simulator HDL ASIC FPGA control systems',
    packages=find_packages(exclude=['docs']),
)
