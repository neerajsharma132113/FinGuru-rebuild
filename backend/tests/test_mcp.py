import asyncio
import pytest
from fastmcp import Client
from mcp_server import mcp


async def call(tool_name, arguments):
    async with Client(mcp) as client:
        return await client.call_tool(tool_name, arguments)


def test_tool_is_listed():
    async def list_names():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            return [tool.name for tool in tools]

    assert "emi_calculator" in asyncio.run(list_names())


def test_emi_tool_matches_the_function():
    result = asyncio.run(call("emi_calculator", {
        "principal": 500000,
        "annual_rate_percent": 10,
        "tenure_months": 60,
    }))
    assert result.data["emi"] == 10623.52
    assert result.data["total_interest"] == 137411.34


def test_emi_tool_rejects_bad_input():
    with pytest.raises(Exception):
        asyncio.run(call("emi_calculator", {
            "principal": -1,
            "annual_rate_percent": 10,
            "tenure_months": 60,
        }))


def test_emi_tool_rejects_huge_tenure():
    with pytest.raises(Exception):
        asyncio.run(call("emi_calculator", {
            "principal": 500000,
            "annual_rate_percent": 10,
            "tenure_months": 601,
        }))