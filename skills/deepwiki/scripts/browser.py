"""
Browser automation module for DeepWiki queries.

This module provides the workflow and helper functions for browser automation.
The actual MCP tool calls (puppeteer_navigate, puppeteer_fill, etc.) are made
by Claude Code during skill execution, not by this script directly.

Architecture:
- This module defines the workflow and data structures
- Claude Code invokes MCP tools based on this workflow
- Results are returned through the defined interfaces
"""

import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse


class BrowserError(Exception):
    """Base exception for browser automation errors."""
    pass


class NavigationError(BrowserError):
    """Raised when navigation fails."""
    pass


class ElementNotFoundError(BrowserError):
    """Raised when an element cannot be located."""
    pass


class TimeoutError(BrowserError):
    """Raised when an operation times out."""
    pass


class ResponseExtractionError(BrowserError):
    """Raised when response extraction fails."""
    pass


def github_to_deepwiki_url(github_url: str) -> str:
    """
    Convert GitHub repository URL to DeepWiki URL.

    Args:
        github_url: GitHub repository URL (e.g., https://github.com/owner/repo)

    Returns:
        DeepWiki URL for the repository

    Examples:
        >>> github_to_deepwiki_url("https://github.com/owner/repo")
        'https://deepwiki.com/github.com/owner/repo'
    """
    # Parse GitHub URL
    parsed = urlparse(github_url)

    # Extract owner and repo from path
    # Path format: /owner/repo
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL format: {github_url}")

    owner = path_parts[0]
    repo = path_parts[1]

    # Construct DeepWiki URL
    # DeepWiki format: https://deepwiki.com/github.com/owner/repo
    deepwiki_url = f"https://deepwiki.com/github.com/{owner}/{repo}"

    return deepwiki_url


def get_query_input_selectors() -> List[str]:
    """
    Get list of possible CSS selectors for the query input field.

    Returns multiple selector strategies as fallback options.

    Returns:
        List of CSS selectors to try in order
    """
    return [
        'input[type="text"]',           # Generic text input
        'textarea',                      # Text area
        'input[placeholder*="query"]',   # Input with "query" in placeholder
        'input[placeholder*="ask"]',     # Input with "ask" in placeholder
        '[role="textbox"]',              # ARIA role textbox
        '.query-input',                  # Class-based selector
        '#query',                        # ID-based selector
    ]


def get_response_container_selectors() -> List[str]:
    """
    Get list of possible CSS selectors for the response container.

    Returns multiple selector strategies as fallback options.

    Returns:
        List of CSS selectors to try in order
    """
    return [
        '.response-container',
        '.answer-box',
        '.result',
        '[role="region"]',
        '.output',
        '#response',
    ]


def get_loading_spinner_selectors() -> List[str]:
    """
    Get list of possible CSS selectors for loading indicators.

    Returns:
        List of CSS selectors for loading indicators
    """
    return [
        '.loading',
        '.spinner',
        '.loader',
        '[aria-busy="true"]',
    ]


def create_response_extraction_script(
    response_selectors: List[str],
    loading_selectors: List[str],
    max_wait_ms: int = 45000,
    poll_interval_ms: int = 1000
) -> str:
    """
    Generate JavaScript code for extracting DeepWiki response.

    This script polls for the response and extracts answer text and sources.

    Args:
        response_selectors: List of CSS selectors for response container
        loading_selectors: List of CSS selectors for loading indicators
        max_wait_ms: Maximum time to wait for response (milliseconds)
        poll_interval_ms: Polling interval (milliseconds)

    Returns:
        JavaScript code as a string

    Note:
        This script runs in the browser context via puppeteer_evaluate.
    """
    # Convert Python lists to JavaScript arrays
    response_selectors_js = str(response_selectors)
    loading_selectors_js = str(loading_selectors)

    script = f"""
(async function() {{
    const maxWait = {max_wait_ms};
    const pollInterval = {poll_interval_ms};
    const responseSelectors = {response_selectors_js};
    const loadingSelectors = {loading_selectors_js};

    let elapsed = 0;

    while (elapsed < maxWait) {{
        // Try to find response container
        let responseContainer = null;
        for (const selector of responseSelectors) {{
            responseContainer = document.querySelector(selector);
            if (responseContainer) break;
        }}

        // Check if loading spinner is present
        let isLoading = false;
        for (const selector of loadingSelectors) {{
            if (document.querySelector(selector)) {{
                isLoading = true;
                break;
            }}
        }}

        // If we have response and not loading, extract data
        if (responseContainer && !isLoading) {{
            // Extract answer text (use textContent for XSS safety)
            const answerText = responseContainer.textContent.trim();

            // Extract source links
            const sourceLinks = Array.from(
                document.querySelectorAll('.sources a, .references a, a[href*="github"]')
            ).map(a => a.href);

            return {{
                success: true,
                answer: answerText,
                sources: sourceLinks,
                elapsed: elapsed
            }};
        }}

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        elapsed += pollInterval;
    }}

    // Timeout reached
    return {{
        success: false,
        error: 'Response timeout',
        elapsed: elapsed
    }};
}})();
"""

    return script


class DeepWikiQueryWorkflow:
    """
    Defines the complete workflow for executing a DeepWiki query.

    This class provides the step-by-step workflow that Claude Code follows
    when executing a query using MCP browser automation tools.
    """

    def __init__(self, github_url: str, query: str, timeout: int = 60):
        """
        Initialize query workflow.

        Args:
            github_url: GitHub repository URL
            query: Query text
            timeout: Query timeout in seconds
        """
        self.github_url = github_url
        self.query = query
        self.timeout = timeout
        self.deepwiki_url = github_to_deepwiki_url(github_url)

    def get_workflow_steps(self) -> List[Dict[str, Any]]:
        """
        Get the complete workflow steps for query execution.

        Returns:
            List of workflow steps with instructions

        This method returns the step-by-step instructions that Claude Code
        follows to execute the query using MCP tools.
        """
        steps = [
            {
                "step": 1,
                "name": "Navigate to DeepWiki",
                "action": "mcp_navigate",
                "params": {
                    "url": self.deepwiki_url
                },
                "description": f"Navigate to {self.deepwiki_url}",
                "error_handling": "Retry up to 3 times with 5s delay"
            },
            {
                "step": 2,
                "name": "Wait for page load",
                "action": "wait",
                "params": {
                    "duration": 2  # seconds
                },
                "description": "Wait for page to fully load"
            },
            {
                "step": 3,
                "name": "Locate query input",
                "action": "find_element",
                "params": {
                    "selectors": get_query_input_selectors()
                },
                "description": "Find query input field using fallback selectors",
                "error_handling": "Try all selectors, raise ElementNotFoundError if none work"
            },
            {
                "step": 4,
                "name": "Enter query text",
                "action": "mcp_fill",
                "params": {
                    "selector": "${input_selector_from_step_3}",
                    "value": self.query
                },
                "description": f"Enter query: {self.query[:50]}..."
            },
            {
                "step": 5,
                "name": "Submit query",
                "action": "submit",
                "params": {
                    "method": "enter_key",  # or "click_button"
                    "selector": "${input_selector_from_step_3}"
                },
                "description": "Submit query by pressing Enter"
            },
            {
                "step": 6,
                "name": "Wait for response",
                "action": "mcp_evaluate",
                "params": {
                    "script": create_response_extraction_script(
                        response_selectors=get_response_container_selectors(),
                        loading_selectors=get_loading_spinner_selectors(),
                        max_wait_ms=self.timeout * 1000
                    )
                },
                "description": "Poll for response and extract answer + sources",
                "error_handling": "Raise TimeoutError if max_wait exceeded"
            },
            {
                "step": 7,
                "name": "Validate response",
                "action": "validate",
                "params": {
                    "required_fields": ["answer", "sources"]
                },
                "description": "Ensure response has required fields"
            },
            {
                "step": 8,
                "name": "Return structured result",
                "action": "format_result",
                "params": {
                    "format": "dict"
                },
                "description": "Return final structured result"
            }
        ]

        return steps

    def get_expected_result_schema(self) -> Dict[str, Any]:
        """
        Get the expected schema for query result.

        Returns:
            Dictionary describing expected result structure
        """
        return {
            "github_url": self.github_url,
            "deepwiki_url": self.deepwiki_url,
            "query": self.query,
            "answer": "string (extracted answer text)",
            "sources": ["list", "of", "source", "URLs"],
            "timestamp": "ISO 8601 timestamp",
            "cached": False,
            "elapsed_seconds": "number"
        }


def simulate_query_execution(github_url: str, query: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Simulate query execution workflow (for testing without browser).

    Args:
        github_url: GitHub repository URL
        query: Query text
        timeout: Timeout in seconds

    Returns:
        Simulated query result

    Note:
        This is for testing only. Actual execution uses MCP tools.
    """
    workflow = DeepWikiQueryWorkflow(github_url, query, timeout)
    steps = workflow.get_workflow_steps()

    return {
        "status": "simulated",
        "message": "This is a simulation. Actual execution requires MCP browser automation.",
        "github_url": github_url,
        "deepwiki_url": workflow.deepwiki_url,
        "query": query,
        "workflow_steps": len(steps),
        "steps": [f"Step {s['step']}: {s['name']}" for s in steps]
    }


# Convenience function for skill execution
def execute_deepwiki_query(
    github_url: str,
    query: str,
    timeout: int = 60,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Execute a DeepWiki query (main entry point for skill execution).

    This function is called by Claude Code during skill execution.
    Claude Code will follow the workflow steps and use MCP tools.

    Args:
        github_url: GitHub repository URL (validated)
        query: Query text (sanitized)
        timeout: Query timeout in seconds (validated)
        verbose: Enable verbose logging

    Returns:
        Query result dictionary

    Raises:
        NavigationError: If navigation fails
        ElementNotFoundError: If query input cannot be found
        TimeoutError: If query times out
        ResponseExtractionError: If response extraction fails

    Note:
        The actual browser automation is performed by Claude Code using
        MCP tools. This function defines the workflow to follow.
    """
    if verbose:
        print(f"Executing DeepWiki query...")
        print(f"  GitHub URL: {github_url}")
        print(f"  Query: {query}")
        print(f"  Timeout: {timeout}s")

    # Create workflow
    workflow = DeepWikiQueryWorkflow(github_url, query, timeout)

    if verbose:
        print(f"  DeepWiki URL: {workflow.deepwiki_url}")
        print(f"  Workflow steps: {len(workflow.get_workflow_steps())}")

    # Return workflow for Claude Code to execute
    # Claude Code will use MCP tools to follow these steps
    return {
        "workflow": workflow,
        "steps": workflow.get_workflow_steps(),
        "expected_schema": workflow.get_expected_result_schema()
    }
