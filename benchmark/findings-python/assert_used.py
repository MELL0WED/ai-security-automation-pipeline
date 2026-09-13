def check_permission(user_role):
    assert user_role == "admin", "Access denied"
    return True
