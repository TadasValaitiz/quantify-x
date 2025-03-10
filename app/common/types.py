from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator


class TradingStrategyDefinition(BaseModel):
    is_strategy: bool = Field(
        default=False,
        description="Whether the user is describing a trading strategy in a way, that it's clear what kinf of strategy is this, and majority of fields are filled",
    )
    strategy_name: Optional[str] = Field(
        default=None,
        description="Concise and descriptive name for the automated trading strategy (2-5 words).",
    )
    strategy_type: Optional[
        Literal[
            "Trend-following",
            "Momentum-based",
            "Reversal",
            "Breakout",
            "Mean Reversion",
            "Volatility-based",
            "Event-driven",
            "Time-based",
            "Hybrid",
        ]
    ] = Field(
        default=None,
        description="The core type of automated trading strategy chosen by the user.",
    )
    assistant_response_summary: Optional[str] = Field(
        description="Detailed summary explaining the assistant's responses and decisions, suitable for the user."
    )
    assistant_reasoning: Optional[List[str]] = Field(
        default_factory=list,
        description="Chronological list of reasoning steps by the assistant, updated with each interaction.",
    )
    trading_idea: Optional[str] = Field(
        description="Detailed explanation of the user's automated trading idea, including rationale and expected edge."
    )
    indicators_and_signals: Optional[List[str]] = Field(
        description="Detailed list of indicators or signals, their calculation, logic, parameters, and their role in the strategy."
    )
    entry_conditions: Optional[List[str]] = Field(
        description="Comprehensive description of entry conditions including indicator thresholds, patterns, and exact logic for automation."
    )
    exit_conditions: Optional[List[str]] = Field(
        description="Detailed explanation of automated exit conditions (take-profit, stop-loss, trailing stop) with risk management logic."
    )
    position_sizing: Optional[str] = Field(
        description="Explicit description of position sizing or money management strategy (fixed size, percentage, volatility-based, etc.)."
    )
    risk_management_rules: Optional[List[str]] = Field(
        description="Specific rules and procedures for managing risk, drawdowns, maximum daily losses, etc."
    )
    markets_and_timeframes: Optional[List[str]] = Field(
        description="Clearly defined markets (stocks, crypto, forex), symbols, exchanges, and precise timeframes or sessions targeted."
    )
    order_types: Optional[List[str]] = Field(
        description="Types of orders used in the strategy (Market, Limit, Stop, Stop-Limit, etc.) and the reasoning behind each type."
    )
    additional_info: Optional[str] = Field(
        description="Additional information about the strategy that is not covered by the other fields."
    )
    questions_about_strategy: Optional[List[str]] = Field(
        description="AI assistant questions about the strategy"
    )
    search_queries: Optional[List[str]] = Field(
        description="Search queries for the strategy"
    )
    source_urls: Optional[List[str]] = Field(description="Source URLs for the strategy")

    # Add validators for list fields to handle string-to-list conversion
    @validator(
        "assistant_reasoning",
        "indicators_and_signals",
        "entry_conditions",
        "exit_conditions",
        "risk_management_rules",
        "markets_and_timeframes",
        "order_types",
        "search_queries",
        "source_urls",
        "questions_about_strategy",
        pre=True,
    )
    def convert_string_to_list(cls, value):
        """Convert a string to a list of strings if provided as a string."""
        if isinstance(value, str):
            # If the string is empty, return an empty list
            if not value.strip():
                return []

            # If the string already looks like a list representation, try to parse it
            if value.startswith("[") and value.endswith("]"):
                try:
                    import ast

                    parsed_value = ast.literal_eval(value)
                    if isinstance(parsed_value, list):
                        return parsed_value
                except (SyntaxError, ValueError):
                    pass

            # Otherwise, treat the string as a single item
            return [value]
        return value

    class Config:
        """Configuration for the Pydantic model."""

        validate_assignment = True
        extra = "ignore"  # Ignore extra fields

    def context_str(self):
        markdown = ""

        if self.strategy_name:
            markdown += f"{self.strategy_name}Strategy type: ({self.strategy_type})\n\n"

        if self.trading_idea:
            markdown += f"Trading Idea\n{self.trading_idea}\n\n"

        if self.indicators_and_signals and len(self.indicators_and_signals) > 0:
            markdown += "Trading Indicators and Signals\n"
            for indicator in self.indicators_and_signals:
                markdown += f"- {indicator}\n"
            markdown += "\n"

        if self.entry_conditions and len(self.entry_conditions) > 0:
            markdown += "Entry Conditions\n"
            for condition in self.entry_conditions:
                markdown += f"* {condition}\n"
            markdown += "\n"

        if self.exit_conditions and len(self.exit_conditions) > 0:
            markdown += "Exit Conditions\n"
            for condition in self.exit_conditions:
                markdown += f"* {condition}\n"
            markdown += "\n"

        if self.markets_and_timeframes and len(self.markets_and_timeframes) > 0:
            markdown += "Target Markets\n"
            for market in self.markets_and_timeframes:
                markdown += f"- {market}\n"
            markdown += "\n"

        if self.order_types and len(self.order_types) > 0:
            markdown += "Order Types\n"
            for order_type in self.order_types:
                markdown += f"- {order_type}\n"
            markdown += "\n"

        if self.risk_management_rules and len(self.risk_management_rules) > 0:
            markdown += "Risk Management Rules\n"
            for risk_management_rule in self.risk_management_rules:
                markdown += f"- {risk_management_rule}\n"
            markdown += "\n"

        if self.position_sizing and len(self.position_sizing) > 0:
            markdown += "Position Sizing\n"
            markdown += f"{self.position_sizing}\n"
            markdown += "\n"

        return markdown

    def to_vector_db_search(self):
        markdown = ""

        if self.trading_idea:
            markdown += f"{self.trading_idea}\n\n"

        if self.entry_conditions and len(self.entry_conditions) > 0:
            for condition in self.entry_conditions:
                markdown += f"{condition}\n"
            markdown += "\n"

        if self.exit_conditions and len(self.exit_conditions) > 0:
            for condition in self.exit_conditions:
                markdown += f"{condition}\n"
            markdown += "\n"

        if self.indicators_and_signals and len(self.indicators_and_signals) > 0:
            for indicator in self.indicators_and_signals:
                markdown += f"{indicator}\n"
            markdown += "\n"

        if self.search_queries and len(self.search_queries) > 0:
            for query in self.search_queries:
                markdown += f"{query}\n"
            markdown += "\n"

        return markdown

