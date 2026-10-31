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

def test_all_three_tools_are_listed():
    async def list_names():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            return [tool.name for tool in tools]

    names = asyncio.run(list_names())
    assert "emi_calculator" in names
    assert "suggest_next_action" in names
    assert "compare_two_loans" in names


def test_next_action_tool_matches_the_function():
    result = asyncio.run(call("suggest_next_action", {
        "monthly_income": 80000,
        "monthly_expenses": 40000,
        "monthly_emi": 10000,
        "emergency_fund": 60000,
    }))
    assert result.data["action"] == "SAVE"
    assert result.data["details"]["emergency_fund_target"] == 120000


def test_compare_tool_matches_the_function():
    result = asyncio.run(call("compare_two_loans", {
        "principal": 500000,
        "annual_rate_percent_a": 10,
        "tenure_months_a": 60,
        "annual_rate_percent_b": 10,
        "tenure_months_b": 36,
    }))
    assert result.data["lower_total_cost"] == "b"
    assert result.data["a"]["emi"] == 10623.52


def test_next_action_tool_rejects_bad_input():
    with pytest.raises(Exception):
        asyncio.run(call("suggest_next_action", {
            "monthly_income": 0,
            "monthly_expenses": 40000,
            "monthly_emi": 10000,
            "emergency_fund": 60000,
        }))