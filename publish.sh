source .venv/bin/activate
echo "Make sure to update the version number beforehand!"
rm -drf dist
python -m build --wheel
rm -drf build
twine upload dist/*