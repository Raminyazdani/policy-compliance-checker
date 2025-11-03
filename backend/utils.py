def normalize_user(raw_user):
    """
    Normalize/derive fields for evaluator. For now: passthrough copy.
    Extend later (e.g., derive password_length, flags, etc.)
    """
    return dict(raw_user)
