import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metrixpp",
    version="1.7.1",
    author="Stefan Strobel",
    author_email="stefan.strobel@shimatta.net",
    description="Metrix++ is an extendable tool for code metrics collection and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metrixplusplus/metrixplusplus",
    packages=setuptools.find_packages(exclude=["metrixpp.tests"]),
    package_data={
        'metrixpp.mpp': ['*.ini'],
        'metrixpp.ext.std': ['*.ini'],
        'metrixpp.ext.std.tools': ['*.ini'],
        'metrixpp.ext.std.code': ['*.ini']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://metrixplusplus.github.io/',
        'Source': 'https://github.com/metrixplusplus/metrixplusplus',
        'Tracker': 'https://github.com/metrixplusplus/metrixplusplus/issues',
    },
    entry_points={
        'console_scripts': [
            'metrix++ = metrixpp.metrixpp:start'
        ]
    },
    python_requires='>=3.5',
)
