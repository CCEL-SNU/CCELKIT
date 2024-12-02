from setuptools import setup, find_packages

setup(
    name="ccelkit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "ase",
        "pillow",
        "scipy",
        "pyyaml",
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'ccelkit=ccelkit.cli:main',
        ],
    },
    python_requires=">=3.6",
    author="CCEL",
    author_email="snupark@snu.ac.kr",
    description="원자 구조 시각화를 위한 POV-Ray 기반 도구",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CCEL-snu/ccelkit",
)