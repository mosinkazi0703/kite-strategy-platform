class PaperBroker:
    """Simulation-only broker. It intentionally has no order placement API."""
    def __init__(self, fill_model): self.fill_model = fill_model
    def fill(self, intent, quote): return self.fill_model.fill(intent, quote)
