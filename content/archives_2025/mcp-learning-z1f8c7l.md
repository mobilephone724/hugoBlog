---
title: MCP学习
slug: mcp-learning-z1f8c7l
url: /post/mcp-learning-z1f8c7l.html
date: '2025-04-08 19:57:51+08:00'
lastmod: '2025-04-12 14:02:15+08:00'
toc: true
isCJKLanguage: true
---



# MCP学习

# 自己对MCP的理解

MCP server (一个简单的程序) 通过定义实现一系列函数，让 MCP client(例如 claude) 通过这些函数，获取到需要的信息。

MCP server:

```python
# in /Users/yby/code/mcp_test/mcp-server-demo/server.py

# List content in my code directory
@mcp.tool()
def list_code_directory() -> str:
    """List content in the code directory"""
    directory = "/Users/yby/code/"
    contents = os.listdir(directory)
    return "\\n".join(contents)
```

MCP client 配置。注意 `uv`​  路径是 full path

```python
{
  "mcpServers": {
    "weather": {
      "command": "/Users/yby/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/yby/code/mcp_test/weather",
        "run",
        "weather.py"
      ]
    },
    "Demo": {
      "command": "/Users/yby/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/Users/yby/code/mcp_test/mcp-server-demo/server.py"
      ]
    }
  }
}
```

# 问题一: MCP client(例如 claude)如何知道调用哪个函数

The MCP (Model Control Protocol) client, such as the Claude desktop application, discovers available functions through a mechanism called function registration and discovery. Here's how it works:

When a server implements MCP functions using the `@mcp.tool()`​ decorator, it creates a standardized description of each function, including:

1. The function name
2. A description of what the function does
3. Parameter specifications (names, types, descriptions, required/optional status)
4. Return type information

During the initial connection or session setup between the client and server, the server sends a capabilities manifest to the client. This manifest contains JSON Schema descriptions of all available functions, which follows the OpenAI function calling format. For example:

```json
{
  "functions": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City and state, e.g., 'San Francisco, CA'"
          }
        },
        "required": ["location"]
      }
    }
  ]
}

```

The client application (Claude desktop) parses this schema to:

1. Know which functions exist and can be called
2. Understand what parameters are required for each function
3. Generate appropriate UI components or code to facilitate calling these functions
4. Validate input before sending function calls to the server

**This architecture allows for dynamic discovery of capabilities - clients don't need to be hardcoded with knowledge of specific functions, and servers can add, modify, or remove functions without requiring client updates**. The client simply adapts to whatever functions the server declares are available.

When you make a request that might benefit from using a function, the Claude model itself might suggest using one of these registered functions, and the client application facilitates this interaction by providing the appropriate interface.
