"""
Deprecated: This module used to provide Perplexity integration.
It has been replaced by tools.openai_insights_tool.fetch_openai_insight.
Left in place temporarily to avoid import errors if any stale references exist.
"""

from tools.openai_insights_tool import fetch_openai_insight as fetch_perplexity_insight  # re-export