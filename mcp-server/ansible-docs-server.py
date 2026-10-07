import json
import subprocess
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

server = Server("ansible-docs-server")

def _run_ansible_doc(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["ansible-doc"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running ansible-doc: {e.stderr}"
    except FileNotFoundError:
        return "Error: ansible-doc command not found. Ensure Ansible is installed."

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="get_module_doc",
            description="Runs ansible-doc <module> and returns the output",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_fqcn": {"type": "string", "description": "The Fully Qualified Collection Name of the module"}
                },
                "required": ["module_fqcn"]
            }
        ),
        Tool(
            name="list_modules",
            description="Lists all modules in a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "The collection name"}
                },
                "required": ["collection"]
            }
        ),
        Tool(
            name="get_module_params",
            description="Returns just the parameters section for a module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_fqcn": {"type": "string", "description": "The Fully Qualified Collection Name of the module"}
                },
                "required": ["module_fqcn"]
            }
        ),
        Tool(
            name="validate_module_exists",
            description="Checks if a module exists",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_fqcn": {"type": "string", "description": "The Fully Qualified Collection Name of the module"}
                },
                "required": ["module_fqcn"]
            }
        ),
        Tool(
            name="search_modules",
            description="Searches modules by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Keyword to search for"}
                },
                "required": ["keyword"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "get_module_doc":
        module = arguments.get("module_fqcn")
        if not module:
            raise ValueError("module_fqcn is required")
        output = _run_ansible_doc([module])
        return [TextContent(type="text", text=output)]
        
    elif name == "list_modules":
        collection = arguments.get("collection")
        if not collection:
            raise ValueError("collection is required")
        output = _run_ansible_doc(["-l", "-t", "module"])
        lines = output.splitlines()
        modules = [line.split()[0] for line in lines if line.startswith(collection)]
        return [TextContent(type="text", text=json.dumps(modules))]
        
    elif name == "get_module_params":
        module = arguments.get("module_fqcn")
        if not module:
            raise ValueError("module_fqcn is required")
        output = _run_ansible_doc([module, "--json"])
        try:
            data = json.loads(output)
            params = data.get(module, {}).get("doc", {}).get("options", {})
            return [TextContent(type="text", text=json.dumps(params, indent=2))]
        except json.JSONDecodeError:
            return [TextContent(type="text", text="Error parsing JSON output from ansible-doc")]
            
    elif name == "validate_module_exists":
        module = arguments.get("module_fqcn")
        if not module:
            raise ValueError("module_fqcn is required")
        result = subprocess.run(["ansible-doc", module], capture_output=True)
        exists = result.returncode == 0
        return [TextContent(type="text", text=str(exists))]
        
    elif name == "search_modules":
        keyword = arguments.get("keyword")
        if not keyword:
            raise ValueError("keyword is required")
        output = _run_ansible_doc(["-l", "-t", "module"])
        lines = output.splitlines()
        modules = [line.split()[0] for line in lines if keyword.lower() in line.lower()]
        return [TextContent(type="text", text=json.dumps(modules))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
