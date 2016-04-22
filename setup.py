from setuptools import setup


setup(
    name='fity',
    version='0.1',
    description='Detect file types based on file content.',
    author='Alexander van Ratingen',
    author_email='alexander@van-ratingen.nl',
    url='https://github.com/alvra/fity',
    packages=[
        'fity',
        'fity.archives',
    ],
    scripts=['fity.py'],
    install_requires=[
        'six',
        # inspecting images
        'pillow',
        # inspecting audio
        'mutagen',
        # detecting scripts
        'pygments',
        # inspecting pdfs
        'PyPDF2',
        'python-dateutil',
        # inspecting fonts
        'fontTools',
        'brotlipy',
        # archives
        'bz2file',
        'rarfile',
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
