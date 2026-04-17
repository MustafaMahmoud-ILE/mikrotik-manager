def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, ""

def validate_password_match(password: str, confirm_password: str) -> tuple[bool, str]:
    if password != confirm_password:
        return False, "Passwords don't match"
    return validate_password(password)
