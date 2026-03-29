from .config import AnalyserConfig


class NetworkAccessError(RuntimeError):
    """Raised when a network-required feature is requested in offline mode."""


def require_network(config: AnalyserConfig) -> None:
    if not config.allow_network:
        raise NetworkAccessError(
            "Network features are disabled. Set allow_network=True to enable outbound calls."
        )
