from setuptools import find_packages, setup

setup(
    name="hookman",
    version="2.0.0",
    description="Git Hooks Manager — instala, gestiona y sincroniza git hooks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Quesillo27",
    author_email="sahidalcantarabarragan@gmail.com",
    url="https://github.com/Quesillo27/git-hooks-manager",
    license="MIT",
    packages=find_packages(include=["hookman", "hookman.*"]),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hookman=hookman.cli:main",
        ],
    },
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Version Control :: Git",
        "Environment :: Console",
        "Intended Audience :: Developers",
    ],
)
