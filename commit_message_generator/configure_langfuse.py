import base64
import os

import logfire
import nest_asyncio  # type: ignore[import-untyped]
from opentelemetry import trace


def scrubbing_callback(match: logfire.ScrubMatch) -> str:
    """Preserve the Langfuse session ID."""
    if (
        match.path == ("attributes", "langfuse.session.id")
        and match.pattern_match.group(0) == "session"
    ):
        # Return the original value to prevent redaction.
        return match.value
    return ""


# Configure Langfuse for agent observability
def configure_langfuse(
    langfuse_public_key: str,
    langfuse_secret_key: str,
    langfuse_host: str = "http://localhost:3002",
) -> trace.Tracer:
    langfuse_auth = base64.b64encode(
        f"{langfuse_public_key}:{langfuse_secret_key}".encode()
    ).decode()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{langfuse_host}/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

    # Configure Logfire to work with Langfuse
    nest_asyncio.apply()
    logfire.configure(
        service_name="commit-msg-gen",
        send_to_logfire=False,
        scrubbing=logfire.ScrubbingOptions(callback=scrubbing_callback),
    )

    return trace.get_tracer("commit-msg-gen")
