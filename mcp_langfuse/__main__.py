import argparse

from .server import build_server


def main() -> None:
    """Punto de entrada CLI: levanta el servidor MCP por stdio (por defecto) o por HTTP."""
    p = argparse.ArgumentParser(prog="mcp_langfuse")
    p.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    server = build_server()
    if a.transport == "stdio":
        server.run(show_banner=True)
    else:
        server.run(transport="http", host=a.host, port=a.port, show_banner=True)


if __name__ == "__main__":
    main()
