from create_app import createApp

app = createApp()

if __name__ == "__main__":
    app.run(debug=True, port=5000)