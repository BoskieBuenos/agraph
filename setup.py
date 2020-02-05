
from distutils.core import setup
version = '0.0.3'
setup(
    name = 'agraph',
    packages = ['agraph'],
    version = version,
    license='TODO', # TODO
    description = 'ASCII graph definition utility',
    author = 'boskiebuenos',
    author_email = '', # TODO
    url = 'https://github.com/BoskieBuenos/agraph',
    download_url = f'https://github.com/BoskieBuenos/agraph/archive/v{version}.tar.gz', # TODO
    keywords = [''], # TODO
    install_requires=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        # 'License :: TODO',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
)
