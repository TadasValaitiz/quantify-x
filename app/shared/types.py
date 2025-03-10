from datetime import datetime
import json
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

# Absolute import from the root common module
from common import TradingStrategyDefinition


class UserStrategy(BaseModel):
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
    followup_questions: Optional[List[str]] = Field(
        default_factory=list,
        description="Specific, unique, and non-repeating follow-up questions posed to clarify aspects of the strategy.",
    )
    direct_answer: Optional[str] = Field(
        description="Direct, detailed, and clear answer from the assistant addressing user's specific questions."
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
        default=None,
        description="Additional information about the strategy that is not covered by the other fields.",
    )

    def message_str(self, short:bool=True):
        markdown = ""

        if short:
            if self.followup_questions and len(self.followup_questions) > 0:
                if self.direct_answer:
                    markdown += f"{self.direct_answer}\n\n"
                markdown += "#### Follow-up Questions\n"
                for i, question in enumerate(self.followup_questions, 1):
                    markdown += f"{i}. {question}\n"
                return markdown

        # Summary if available
        if self.assistant_response_summary:
            markdown += f"#### Summary\n{self.assistant_response_summary}\n\n"

        # Add reasoning if available (in a Streamlit-friendly format)
        if self.assistant_reasoning and len(self.assistant_reasoning) > 0:
            markdown += "#### Reasoning\n"
            for reasoning in self.assistant_reasoning:
                markdown += f"* {reasoning}\n\n"

        # Main trading strategy information
        if self.trading_idea:
            if self.strategy_type:
                markdown += f"#### Strategy ({self.strategy_type})\n\n"
            markdown += f"###### Trading Idea\n{self.trading_idea}\n\n"

        # Trading indicators with bullet points
        if self.indicators_and_signals and len(self.indicators_and_signals) > 0:
            markdown += "#### Trading Indicators and Signals\n"
            for indicator in self.indicators_and_signals:
                markdown += f"* {indicator}\n"
            markdown += "\n"

        # Entry conditions with bullet points
        if self.entry_conditions and len(self.entry_conditions) > 0:
            markdown += "#### Entry Conditions\n"
            for condition in self.entry_conditions:
                markdown += f"* {condition}\n"
            markdown += "\n"

        # Exit conditions with bullet points
        if self.exit_conditions and len(self.exit_conditions) > 0:
            markdown += "#### Exit Conditions\n"
            for condition in self.exit_conditions:
                markdown += f"* {condition}\n"
            markdown += "\n"

        # Markets with bullet points
        if self.markets_and_timeframes and len(self.markets_and_timeframes) > 0:
            markdown += "#### Target Markets\n"
            for market in self.markets_and_timeframes:
                markdown += f"* {market}\n"
            markdown += "\n"

        if self.order_types and len(self.order_types) > 0:
            markdown += "#### Order Types\n"
            for order_type in self.order_types:
                markdown += f"* {order_type}\n"
            markdown += "\n"

        if self.risk_management_rules and len(self.risk_management_rules) > 0:
            markdown += "#### Risk Management Rules\n"
            for risk_management_rule in self.risk_management_rules:
                markdown += f"* {risk_management_rule}\n"
            markdown += "\n"

        if self.position_sizing and len(self.position_sizing) > 0:
            markdown += "#### Position Sizing\n"
            markdown += f"{self.position_sizing}\n"
            markdown += "\n"

        if self.direct_answer:
            markdown += "---\n"
            markdown += f"{self.direct_answer}\n\n"

        return markdown

    def context_str(self):
        markdown = ""

        # Main trading strategy information
        if self.trading_idea:
            if self.strategy_type:
                markdown += f"Strategy ({self.strategy_type})\n\n"
            markdown += f"Trading Idea\n{self.trading_idea}\n\n"

        # Trading indicators with bullet points
        if self.indicators_and_signals and len(self.indicators_and_signals) > 0:
            markdown += "Trading Indicators and Signals\n"
            for indicator in self.indicators_and_signals:
                markdown += f"- {indicator}\n"
            markdown += "\n"

        # Entry conditions with bullet points
        if self.entry_conditions and len(self.entry_conditions) > 0:
            markdown += "Entry Conditions\n"
            for condition in self.entry_conditions:
                markdown += f"- {condition}\n"
            markdown += "\n"

        # Exit conditions with bullet points
        if self.exit_conditions and len(self.exit_conditions) > 0:
            markdown += "Exit Conditions\n"
            for condition in self.exit_conditions:
                markdown += f"- {condition}\n"
            markdown += "\n"

        # Markets with bullet points
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

        if self.followup_questions and len(self.followup_questions) > 0:
            markdown += "Previous Followup Questions\n"
            markdown += "If user answers these questions, don't repeat in your answer\n"
            for i, question in enumerate(self.followup_questions, 1):
                markdown += f"{i}. {question}\n"
            markdown += "\n"

        return markdown

    def followup_str(self):
        markdown = ""
        if self.followup_questions and len(self.followup_questions) > 0:
            markdown += "Previous Followup Questions\n"
            for i, question in enumerate(self.followup_questions, 1):
                markdown += f"{i}. {question}\n"
        return markdown


class RouteContext(BaseModel):
    message_type: Optional[
        Literal["non-related", "follow-up", "instruction", "question", "evaluation"]
    ] = Field(
        default="non-related",
        description="Message type based on user input",
    )


class QaContext(BaseModel):
    question: str
    answer: Optional[str]


class EvaluationContext(BaseModel):
    positive_points: Optional[List[str]]
    negative_points: Optional[List[str]]
    score: Optional[int]

    def to_message_str(self):
        markdown = "### Evaluation:\n"

        # Add reasoning if available (in a Streamlit-friendly format)
        if self.positive_points and len(self.positive_points) > 0:
            markdown += "#### Positive points:\n"
            for points in self.positive_points:
                markdown += f"* {points}\n"
            markdown += "\n"

        if self.negative_points and len(self.negative_points) > 0:
            markdown += "#### Negative points:\n"
            for points in self.negative_points:
                markdown += f"* {points}\n"
            markdown += "\n"

        if self.score:
            markdown += f"#### Score: {self.score}\n"

        return markdown


class ContextDict(BaseModel):
    user_strategy: Optional[UserStrategy]
    rag_strategies: List[TradingStrategyDefinition]
    route: Optional[RouteContext]
    conversations: List[QaContext]
    evaluation: Optional[EvaluationContext]

    @classmethod
    def empty(cls) -> "ContextDict":
        return cls(
            user_strategy=None,
            rag_strategies=[],
            route=None,
            conversations=[],
            evaluation=None,
        )
        
    def new_run(self):
        return ContextDict(
            user_strategy=self.user_strategy,
            rag_strategies=[],
            route=None,
            conversations=self.conversations,
            evaluation=None,
        )
    
    def last_qa(self):
        return self.conversations[-1] if len(self.conversations) > 0 else None

    def last_qa_answer(self):
        last_qa = self.last_qa()
        return last_qa.answer if last_qa else ""

    def to_full_strategy_context(self):
        return self.user_strategy.context_str() if self.user_strategy else ""

    def conversation_context(self, number_of_questions: int = 3):
        markdown = ""
        if len(self.conversations) > 0:
            markdown += "Conversation History\n\n"
            for conversation in self.conversations[-number_of_questions:]:
                markdown += f"Question: {conversation.question}\n\n"
                markdown += f"Answer:{conversation.answer}\n\n"
                markdown += "----\n"
        return markdown

    def router_context(self):
        return self.strategy_with_conversation()

    def rag_context(self):
        markdown = ""
        if self.rag_strategies:
            markdown += "Strategies from RAG for ideas\n\n"
            for strategy in self.rag_strategies:
                markdown += strategy.context_str()
                markdown += "----\n"
        markdown += self.conversation_context(number_of_questions=2)
        return markdown

    def strategy_with_rag(self):
        markdown = ""
        if self.user_strategy:
            markdown += "User Generated Strategy\n\n"
            markdown += self.user_strategy.context_str()
        markdown += self.rag_context()

        return markdown

    def strategy_with_conversation(self):
        markdown = ""
        if self.user_strategy:
            markdown += "User Generated Strategy\n\n"
            markdown += self.user_strategy.context_str()
            markdown += "\n\n"
        markdown += self.conversation_context(number_of_questions=2)
        return markdown

    def to_message_str(self):
        msg = ""
        last_qa_answer = self.last_qa_answer()

        if self.route and self.route.message_type:
            if self.route.message_type == "non-related":
                if last_qa_answer:
                    msg += last_qa_answer
            elif self.route.message_type == "instruction":
                if self.user_strategy:
                    msg += self.user_strategy.message_str()
            elif self.route.message_type == "follow-up":
                if self.user_strategy:
                    msg += self.user_strategy.message_str()
            elif self.route.message_type == "question":
                if last_qa_answer:
                    msg += last_qa_answer
            elif self.route.message_type == "evaluation":
                if self.user_strategy:
                    msg += self.user_strategy.message_str()
                if self.evaluation:
                    msg += self.evaluation.to_message_str()
        return msg


class ChatMessage(BaseModel):
    id: Optional[int]
    conversation_id: int
    role: str
    content: str
    context: Optional[ContextDict] = None
    created_at: str

    def __init__(
        self,
        id: Optional[int],
        conversation_id: int,
        role: str,
        content: str,
        context: Optional[ContextDict],
        created_at: str,
    ):
        super().__init__(
            id=id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            context=context,
            created_at=created_at,
        )

    def to_message_str(self):
        if self.context:
            return self.context.to_message_str()
        return self.content

    @classmethod
    def from_dict(cls, message: Dict[str, Any]):
        id = message["id"]
        conversation_id = message["conversation_id"]
        role = message["role"]
        content = message["content"]
        context = (
            json.loads(message["context"]) if message["context"] is not None else None
        )
        created_at = message["created_at"]
        context_dict = ContextDict(**context) if context else None
        return cls(id, conversation_id, role, content, context_dict, created_at)

    @classmethod
    def new_message(
        cls,
        conversation_id: int,
        role: str,
        content: str,
        context: Optional[ContextDict],
    ):
        created_at = datetime.now().isoformat()
        return cls(None, conversation_id, role, content, context, created_at)
