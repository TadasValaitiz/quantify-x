from datetime import datetime
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TradingContextCollection(BaseModel):
    trading_topic: bool = Field(
        default=False,
        description="Whether the topic is about trading, or not related and user needs to be returned to trading topic",
    )
    name_of_conversation: Optional[str] = Field(
        default=None,
        description="Name of 1-3 words of trading strategy if name not exist",
    )
    assistant_response_summary: Optional[str] = Field(
        description="Summary of the assistant response, use long form, that will be presented to user"
    )
    assistant_reasoning: Optional[List[str]] = Field(
        description="AI Assistant reasoning steps, if reasoning exist in context, append to this list"
    )
    followup_questions: Optional[List[str]] = Field(
        description="Followup questions to the user, if any fields are not clear for trading strategy, these questions are uniq and cannot be repeated"
    )
    direct_answer: Optional[str] = Field(
        description="Direct AI assistant answer when user ask questions, clarifies about strategy, or wants additional information",
    )
    trading_idea: Optional[str] = Field(
        description="Trading idea, a paragraph about trading idea, how it might work"
    )
    trading_indicators: Optional[List[str]] = Field(
        description="Trading indicators with short description how they work"
    )
    entry_conditions: Optional[List[str]] = Field(
        description="Long form information about Entry conditions, Risk management, stop loss/take profit."
    )
    exit_conditions: Optional[List[str]] = Field(
        description="Long form information about Exit conditions, Risk management, stop loss/take profit"
    )
    markets_and_timeframes: Optional[List[str]] = Field(
        description="Markets which user wants to trade, trading windows, trading hours anything related with market regime"
    )
    user_inputs: List[str] = Field(
        default=[],
        description="User inputs, if previous input exist, AI assistant needs to append to this list",
    )
    confirmed: bool = Field(
        default=False,
        description="User explicit confirmation that this strategy is good, don' fill this field without user confirmation",
    )

    def to_conversation_message(self):
        markdown = ""

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
            markdown += f"#### Trading Idea\n{self.trading_idea}\n\n"

        # Trading indicators with bullet points
        if self.trading_indicators and len(self.trading_indicators) > 0:
            markdown += "#### Trading Indicators\n"
            for indicator in self.trading_indicators:
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

        if self.direct_answer:
            markdown += "---\n"
            markdown += f"{self.direct_answer}\n\n"

        if not self.confirmed:
            markdown += f"\nDo you Confirm this strategy? If yes, write Confirm\n"

        return markdown

    def to_prompt_context(self):
        markdown = ""

        # Add reasoning if available (in a Streamlit-friendly format)
        if self.assistant_reasoning and len(self.assistant_reasoning) > 0:
            markdown += "#### Reasoning\n"
            for reasoning in self.assistant_reasoning:
                markdown += f"* {reasoning}\n\n"

        # Main trading strategy information
        if self.trading_idea:
            markdown += f"#### Trading Idea\n{self.trading_idea}\n\n"

        # Trading indicators with bullet points
        if self.trading_indicators and len(self.trading_indicators) > 0:
            markdown += "#### Trading Indicators\n"
            for indicator in self.trading_indicators:
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

        # User inputs with bullet points
        if self.user_inputs and len(self.user_inputs) > 0:
            markdown += "#### User Inputs\n"
            for user_input in self.user_inputs:
                markdown += f"* {user_input}\n"
            markdown += "\n"

        if self.followup_questions and len(self.followup_questions) > 0:
            markdown += "#### Previous Followup Questions\n"
            markdown += "If user answers these questions, don't repeat in your answer\n"
            for i, question in enumerate(self.followup_questions, 1):
                markdown += f"{i}. {question}\n"
            markdown += "\n"

        return markdown


class ContextDict(BaseModel):
    trading_context: Optional[TradingContextCollection]

    def to_prompt_context(self):
        return (
            self.trading_context.to_prompt_context() if self.trading_context else None
        )

    def to_conversation_message(self):
        return (
            self.trading_context.to_conversation_message()
            if self.trading_context
            else None
        )


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

    def to_conversation_message(self):
        if self.context:
            return self.context.to_conversation_message()
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
