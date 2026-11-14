from .roles import Role


class AccessPolicy:
    allowed_actions = frozenset()

    def can(self, action):
        return action in self.allowed_actions


class ManagerPolicy(AccessPolicy):
    def can(self, action):
        return True


class GeneratorPolicy(AccessPolicy):
    allowed_actions = frozenset({"view_equipment", "edit_equipment"})


class ExecutorPolicy(AccessPolicy):
    allowed_actions = frozenset({"create_alert", "change_status", "view_equipment"})


class AnalystPolicy(AccessPolicy):
    allowed_actions = frozenset({"view_stats", "view_reports", "view_equipment"})


POLICIES = {
    Role.MANAGER: ManagerPolicy(),
    Role.GENERATOR: GeneratorPolicy(),
    Role.EXECUTOR: ExecutorPolicy(),
    Role.ANALYST: AnalystPolicy(),
}


def can(user, action):
    policy = POLICIES.get(user.role)
    return policy.can(action) if policy else False