from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys

class CustomInstallCommand(install):
    def run(self):
        # Run the standard install
        install.run(self)
        # Install the custom package
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
                               'https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_core_sci_sm-0.5.0.tar.gz'])


with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name="ecg_image_kit",
    version="0.0.22",
    description="A toolkit for synthesis, analysis, and digitization of electrocardiogram images",
    long_description=open('README.md').read(),  # Assuming you have a README.md file
    long_description_content_type='text/markdown',  # Specify the format of the long description
    packages=find_packages(where='src'),  # Automatically find packages in the directory
    package_dir={'': 'src'},
    include_package_data=True,  # Include files specified in MANIFEST.in
    install_requires=required_packages,  # Install dependencies from requirements.txt
    license="MIT",  # Specify your license
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    keywords=["ecg", "image", "analysis", "synthesis", "digitization"],
    python_requires='>=3.9',  # Specify the required Python version
    url="https://github.com/alphanumericslab/ecg-image-kit",  # Homepage URL
    project_urls={
        "Homepage": "https://github.com/alphanumericslab/ecg-image-kit",
        "Issues": "https://github.com/alphanumericslab/ecg-image-kit/issues",
    },
)