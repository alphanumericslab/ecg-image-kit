from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name="ecg_image_kit",
    version="0.0.16",
    description="A toolkit for synthesis, analysis, and digitization of electrocardiogram images",
    long_description=open('README.md').read(),  # Assuming you have a README.md file
    long_description_content_type='text/markdown',  # Specify the format of the long description
    packages=find_packages(),  # Automatically find packages in the directory
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
    keywords=["ecg", "image", "analysis", "synthesis", "digitization"],
    python_requires='>=3.9',  # Specify the required Python version
    url="https://github.com/alphanumericslab/ecg-image-kit",  # Homepage URL
    project_urls={
        "Homepage": "https://github.com/alphanumericslab/ecg-image-kit",
        "Issues": "https://github.com/alphanumericslab/ecg-image-kit/issues",
    },
)