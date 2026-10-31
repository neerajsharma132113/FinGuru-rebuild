from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.services.finance import summarize_by_month, next_best_action


class HealthState(TypedDict, total=False):
    transactions: list
    monthly_emi: float
    emergency_fund: float
    months: list
    latest: dict
    trend: str
    advice: dict
    result: dict


def summarize_step(state):
    return {"months": summarize_by_month(state["transactions"])}


def route_after_summary(state):
    if len(state["months"]) == 0:
        return "no_data"
    if state["months"][-1]["income"] <= 0:
        return "no_income"
    return "continue"


def no_data_step(state):
    return {"result": {"status": "no_data", "message": "Add some transactions first."}}


def no_income_step(state):
    latest = state["months"][-1]
    return {
        "result": {
            "status": "no_income",
            "month": latest["month"],
            "message": "The latest month has no income recorded, so a check is not possible.",
        }
    }


def trend_step(state):
    months = state["months"]
    latest = months[-1]

    if len(months) < 2:
        trend = "not enough data"
    else:
        change = latest["savings"] - months[-2]["savings"]
        if change > 0:
            trend = "improving"
        elif change < 0:
            trend = "worsening"
        else:
            trend = "flat"

    return {"latest": latest, "trend": trend}


def advice_step(state):
    latest = state["latest"]
    advice = next_best_action(
        latest["income"], latest["expenses"], state["monthly_emi"], state["emergency_fund"]
    )
    return {"advice": advice}


def finish_step(state):
    latest = state["latest"]
    advice = state["advice"]
    return {
        "result": {
            "status": "ok",
            "month": latest["month"],
            "income": latest["income"],
            "expenses": latest["expenses"],
            "savings": latest["savings"],
            "savings_rate_percent": latest["savings_rate_percent"],
            "savings_trend": state["trend"],
            "action": advice["action"],
            "reason": advice["reason"],
            "details": advice["details"],
        }
    }


# Build the graph: add the steps, then connect them
graph = StateGraph(HealthState)
graph.add_node("summarize_step", summarize_step)
graph.add_node("no_data_step", no_data_step)
graph.add_node("no_income_step", no_income_step)
graph.add_node("trend_step", trend_step)
graph.add_node("advice_step", advice_step)
graph.add_node("finish_step", finish_step)

graph.add_edge(START, "summarize_step")
graph.add_conditional_edges(
    "summarize_step",
    route_after_summary,
    {"no_data": "no_data_step", "no_income": "no_income_step", "continue": "trend_step"},
)
graph.add_edge("trend_step", "advice_step")
graph.add_edge("advice_step", "finish_step")
graph.add_edge("no_data_step", END)
graph.add_edge("no_income_step", END)
graph.add_edge("finish_step", END)

health_graph = graph.compile()


def run_health_graph(transactions, monthly_emi, emergency_fund):
    final_state = health_graph.invoke({
        "transactions": transactions,
        "monthly_emi": monthly_emi,
        "emergency_fund": emergency_fund,
    })
    return final_state["result"]