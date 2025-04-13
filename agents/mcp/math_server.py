# math_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

mcp.settings.port = 8001

@mcp.tool()
async def add(a:int, b:int) -> int:
    """use this tool to add two numbers, sum two numbers, addition of two numbers or when user ask for any total number."""
    print("calling add")
    return (a + b)

@mcp.tool()
async def minus(a:int, b:int) -> int:
    """use this tool to minus two numbers, deduct betwee two numbers, user or someone gave something to others then how many
left with user or someone."""
    print("calling Minus")
      if a> b :
        return (a-b)
      else: return(b-a)


@mcp.tool()
async def multi(a:int, b:int) -> int:
    print("calling Multi")
    """use this tool to multiply two numbers, cross product of two numbers."""
    return (a * b)

if __name__ == "__main__":
    mcp.run(transport="sse")
    # To run the server, use the command: python math_server.py
    # Then, you can call the tools using the FastMCP client