from setuptools import setup, find_packages

setup(
    name="mfee-eval",
    version="1.0.0",
    description="MFEE Evaluation Harness - Avoid ~75% of Transformer Inference",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Anima Core Inc",
    author_email="contact@animacore.com",
    url="https://github.com/animacore/mfee-eval",
    packages=find_packages(),
    install_requires=[
        "torch>=1.9.0",
        "numpy>=1.21.0",
        "pyyaml>=5.4.0",
        "requests>=2.25.0",
        "jsonlines>=2.0.0",
        "matplotlib>=3.3.0",
        "tqdm>=4.60.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mfee-run=mfee_eval.cli.mfee_run:main",
            "mfee-report=mfee_eval.cli.mfee_report:main",
            "mfee-replay=mfee_eval.cli.mfee_replay:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)