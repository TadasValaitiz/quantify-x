chain = router_chain | RunnableBranch(
    (lambda c: route_type(c) == "non-related", general_message_chain),
    (lambda c: route_type(c) == "instruction", instruction_chain),
    (
        lambda c: route_type(c) == "question",
        question_chain,
    ),
    (
        lambda x: route_type(x) == "evaluation",
        RunnableLambda(
            partial(input, fn=lambda c: c.to_full_strategy_context())
        )
        | evaluation_chain,
    ),
    general_message_chain,  # Default case if none of the conditions match
) 