echo "BUILD START"

# Create a virtual environment for the build process (PEP 668 fix)
python3 -m venv venv_build
source venv_build/bin/activate

# Install requirements
pip install -r requirements.txt

# Run migrations automatically during build
echo "Running migrations..."
python3 manage.py migrate --noinput

# Run collectstatic
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"
