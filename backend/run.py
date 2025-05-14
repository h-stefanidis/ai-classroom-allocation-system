from create_app import createApp
import sys,os
# Add project root to sys.path so 'db' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app = createApp()

if __name__ == "__main__":
    app.run(debug=True, port=5000)