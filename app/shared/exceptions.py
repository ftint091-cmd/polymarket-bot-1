class BotError(Exception):
    """Base bot error"""

class ConfigError(BotError):
    """Configuration error"""

class ExecutionError(BotError):
    """Execution layer error"""

class RiskRejected(BotError):
    """Trade rejected by risk layer"""

class InvalidCommandError(BotError):
    """Command not valid in current lifecycle state"""

class SecretsError(BotError):
    """Secrets retrieval error"""

class MarketDataError(BotError):
    """Market data retrieval error"""
