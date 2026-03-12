

import argparse
from routes_mcp import mcp   # FastMCP instance พร้อม tools ทั้งหมด


def parse_args():
    parser = argparse.ArgumentParser(description="JamorCineplex MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host สำหรับ SSE / HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port สำหรับ SSE / HTTP transport (default: 8001)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.transport == "stdio":
        # รันแบบ stdio — มาตรฐานสำหรับ Claude Desktop
        mcp.run(transport="stdio")

    elif args.transport == "sse":
        # รันแบบ SSE — เข้าถึงผ่าน http://<host>:<port>/sse
        mcp.run(transport="sse", host=args.host, port=args.port)

    else:
        # รันแบบ Streamable HTTP (fastmcp >= 2.x)
        # เข้าถึงผ่าน http://<host>:<port>/mcp
        mcp.run(transport="streamable-http", host=args.host, port=args.port)