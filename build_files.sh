echo "BUILD START"

# Create a virtual environment for the build process (PEP 668 fix)
python3 -m venv venv_build
source venv_build/bin/activate

# Install requirements
pip install -r requirements.txt

# Run collectstatic
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
