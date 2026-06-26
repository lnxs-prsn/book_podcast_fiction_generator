"""Section 4: call_api — send prompt + PDF text to the LLM and return the reply."""

from llm.exceptions import LLMError
from llm.protocol import LLMClient

from .exceptions import ScriptGenerationError


def call_api(pdf_text: str, prompt_text: str, llm: LLMClient, timeout: float = 120.0) -> str:
    """Send an assembled prompt to the injected LLM client and return the reply.

    The "---" separator between the prompt and PDF text is a podcast-domain
    convention; it is assembled here before calling the generic client.
    """
    combined = f"{prompt_text}\n\n---\n\n{pdf_text}" if pdf_text else prompt_text
    try:
        return llm.call(prompt=combined, timeout=timeout)
    except LLMError as e:
        raise ScriptGenerationError(str(e)) from e
