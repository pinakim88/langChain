# weather_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> int:
    """Get the current weather for location."""
    # Simulate fetching weather data
    return f"The current weather in {location} is sunny with a temperature of 25°C."

if __name__ == "__main__":
    mcp.run(transport="sse")
    # To run the server, use the command: python weather_server.py
    # Then, you can call the get_weather tool using the FastMCP client.transport