from flask import Flask, render_template
import socket
import os


app = Flask(__name__)

@app.route("/")
def home():
    hostname = os.environ.get("COMMIT_HASH", "unknown")
    commit_hash = os.environ.get("COMMIT_HASH", "unknown")
    return f"""
        <h1>Multi VM Deployment App</h1>
        <p><strong>Running on host:</strong> {hostname}</p>
        <p><strong>Git commit hash:</strong> {commit_hash}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)