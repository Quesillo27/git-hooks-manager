from setuptools import setup

setup(
    name="hookman",
    version="1.0.0",
    description="Git Hooks Manager — instala y gestiona git hooks entre proyectos",
    author="Quesillo27",
    py_modules=["hookman"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hookman=hookman:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
