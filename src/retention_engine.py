def retention_strategy(data: dict, churn_prob: float) -> str:
    contract = data.get("Contract", "Month-to-month")
    internet_service = data.get("InternetService", "DSL")
    monthly_charges = float(data.get("MonthlyCharges", 0))

    if churn_prob >= 0.75:
        if contract == "Month-to-month":
            return "Offer a 20% loyalty discount and move the customer to a longer contract."
        if internet_service == "Fiber optic":
            return "Assign a retention specialist and bundle premium support for service assurance."
        return "Trigger an urgent save campaign with discount, account review, and proactive support."

    if churn_prob >= 0.45:
        if monthly_charges > 80:
            return "Recommend a lower-cost plan review and personalized add-on optimization."
        return "Offer a retention check-in with plan comparison and service usage coaching."

    return "Customer looks stable. Keep them engaged with routine value messaging and loyalty rewards."
