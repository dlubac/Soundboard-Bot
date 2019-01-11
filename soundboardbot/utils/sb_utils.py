def has_role(member, role_name: str) -> bool:
    """
    Determines if a user has a role
    :param member: Guild member
    :param role_name: Name of role
    :return: Bool indicating if member has role
    """
    roles = [role.name for role in member.roles]
    return role_name in roles
