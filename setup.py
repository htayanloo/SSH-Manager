from setuptools import setup, find_packages

setup(
    name="sshmgm",
    version="1.0.2",
    description="A tool for parsing and displaying SSH connection history",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Hadi Tayanloo",
    author_email="htayanloo@example.com",
    url="https://github.com/htayanloo/SSH-Manager",  # Replace with your GitHub repository link
    packages=find_packages(),
    install_requires=[
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "sshmgm-parser=ssh_manager.parser:main",
            "sshmgm=ssh_manager.viewer:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
