import argparse
from routes_mcp import mcp 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio")
    args = parser.parse_args()

    # รันผ่าน stdio เพื่อให้ Claude Desktop ติดต่อผ่าน Command Line ได้โดยตรง
    if args.transport == "stdio":
        mcp.run(transport="stdio")