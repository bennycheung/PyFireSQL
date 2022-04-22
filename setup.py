from setuptools import setup, find_packages

setup(
    name='pyfiresql',
    version='0.2.5',
    description='Firestore SQL-like query tools.',
    author='Benny Cheung',
    author_email='btscheung@gmail.com',
    url='https://github.com/bennycheung/PyFireSQL',
    download_url='',
    license='MIT',
    packages=find_packages(exclude=['tests', 'images']),
    keywords=['Firebase', 'Firestore', 'SQL'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data = {'': ['*.md', '*.lark']},
    python_requires='>=3.6',
    install_requires=[
        'firebase-admin',
        'lark',
        'matplotlib',
        'numpy'
    ]
)

