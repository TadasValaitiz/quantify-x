"""
Discord scraper package for fetching and processing messages.
"""

__all__ = ['scrape_channel']

def __getattr__(name):
    if name == 'scrape_channel':
        from .discord_scraper import scrape_channel
        return scrape_channel
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
