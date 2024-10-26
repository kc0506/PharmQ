from textual_serve.server import Server

# Server("uv run -m pharmq.app").serve()
Server(
    "python3 -m pharmq.app",
    host="0.0.0.0",
    port=7414,
    public_url="https://pharmq.onrender.com",
).serve()
