import datetime

class CooldownCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cooldowns = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_cooldown(self, user_id, server_id, cooldown_end_time):
        """Set a user's cooldown end time."""
        self.cooldowns[(user_id, server_id)] = cooldown_end_time

    def check_cooldown(self, user_id, server_id):
        """Check if a user is on cooldown."""
        current_time = datetime.datetime.now()
        cooldown_end_time = self.cooldowns.get((user_id, server_id))
        if cooldown_end_time and current_time < cooldown_end_time:
            return True, cooldown_end_time  # User is on cooldown
        return False, None  # User is not on cooldown or no cooldown set
