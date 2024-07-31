create dist
```
python setup.py sdist bdist_wheel
```

Upload to test pYPI:
```
twine upload --repository testpypi dist/*
```

Install from test PYPI:
```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ecg-image-kit==0.0.20
```

