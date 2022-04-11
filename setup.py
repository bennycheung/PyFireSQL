from setuptools import setup, find_packages

setup(
    name='firesql',
    version='0.1.0',
    description='Firebase backend client and computation tools.',
    author='Benny Cheung',
    author_email='btscheung@gmail.com',
    url='https://bennycheung.github.io',
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

