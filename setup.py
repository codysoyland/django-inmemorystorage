import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(
    name = "django-inmemorystorage",
    version = "0.1.0",
    url = 'http://github.com/codysoyland/django-inmemorystorage',
    license = 'BSD',
    description = "A non-persistent in-memory data storage backend for Django.",
    long_description = README,
    author = 'Cody Soyland',
    author_email = 'cody@soyland.com',
    packages = [
        'inmemorystorage',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
