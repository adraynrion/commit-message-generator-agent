"""Commit message generator implementation using Pydantic AI with Langfuse integration."""

import logging
import os
from typing import Any, Dict, Optional

from pydantic_ai import Agent

# Try to import Langfuse, but make it optional
try:
    from langfuse import Langfuse
    LANG_FUSE_AVAILABLE = True
except ImportError:
    LANG_FUSE_AVAILABLE = False

from commit_message_generator.config import GeneratorConfig
from commit_message_generator.models import CommitMessageResponse

# Configure logging
logger = logging.getLogger(__name__)

# Default system prompt template
DEFAULT_SYSTEM_PROMPT = """# Git Commit Message Generator

## Role
You are an expert software developer and Git user. Your task is to analyze code changes and generate clear, concise, and meaningful commit messages.

## Commit Message Guidelines
1. **Format**: `<type>/<severity>: <ticket> - <description>`
2. **Structure**:
   - Title line (max 50 chars)
   - Blank line
   - Detailed description (wrap at {max_line_length} chars)
   - Reference to related issues (if any)
3. **Language**: English only

## Change Analysis
Carefully analyze the provided diff to understand:
- What was changed
- Why it was changed
- Impact of the changes
- Any potential risks or considerations

## Output
Generate a commit message that follows the specified format and guidelines."""


class CommitMessageGenerator:
    """AI-powered commit message generator.

    This agent generates commit messages based on git changes and a system prompt. It
    follows the conventional commit format and includes ticket numbers when available.

    """

    def __init__(
        self,
        config: Optional[GeneratorConfig] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        """Initialize the commit message generator.

        Args:
            config: Configuration for the generator. If None, default config is used.
            system_prompt: Custom system prompt. If None, default is used.

        """
        self.config = config or GeneratorConfig()
        self.system_prompt = self._build_system_prompt(system_prompt)
        self.ai = self._init_ai()

    def _init_ai(self) -> Agent:
        """Initialize the AI client with configuration and Langfuse integration if enabled."""
        # Initialize Langfuse if enabled and available
        logger.debug(f"Checking Langfuse configuration: hasattr(self.config, 'langfuse')={hasattr(self.config, 'langfuse')}")
        if hasattr(self.config, 'langfuse'):
            logger.debug(f"Langfuse config: {self.config.langfuse}")
            logger.debug(f"Langfuse enabled: {getattr(self.config.langfuse, 'enabled', False)}")

        if hasattr(self.config, 'langfuse') and self.config.langfuse and getattr(self.config.langfuse, 'enabled', False) and LANG_FUSE_AVAILABLE:
            try:
                # Get credentials from config or environment variables
                public_key = (
                    self.config.langfuse.public_key or
                    os.getenv("LANGFUSE_PUBLIC_KEY")
                )
                secret_key = (
                    self.config.langfuse.secret_key or
                    os.getenv("LANGFUSE_SECRET_KEY")
                )
                host = (
                    self.config.langfuse.host or
                    os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                )

                if not public_key or not secret_key:
                    logger.warning(
                        "Langfuse is enabled but missing required credentials. "
                        "Please set public_key and secret_key in the config or environment variables."
                    )
                else:
                    # Initialize Langfuse client
                    self.langfuse = Langfuse(
                        public_key=public_key,
                        secret_key=secret_key,
                        host=host,
                    )

                    # Test the connection
                    try:
                        self.langfuse.auth_check()
                        logger.info("Langfuse tracing initialized successfully")
                    except Exception as auth_error:
                        logger.warning(f"Langfuse auth check failed: {str(auth_error)}")
                        if hasattr(self, 'langfuse'):
                            delattr(self, 'langfuse')

            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {str(e)}")
                if hasattr(self, 'langfuse'):
                    delattr(self, 'langfuse')

        try:
            ai_config = self.config.ai
            logger.debug(f"Initializing AI with config: {ai_config}")

            # Get the API key from environment variable
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                error_msg = "OPENAI_API_KEY environment variable is not set"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Using model: {ai_config.model_name}")

            # Initialize the AI agent with explicit API key
            agent = Agent(
                model=ai_config.model_name,
                temperature=ai_config.temperature,
                max_tokens=ai_config.max_tokens,
                top_p=ai_config.top_p,
                api_key=api_key,  # Explicitly pass the API key
            )

            logger.debug("AI agent initialized successfully")
            return agent

        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to initialize AI agent: {str(e)}") from e

    def _build_system_prompt(self, custom_prompt: Optional[str] = None) -> str:
        """Build the system prompt with configuration values.

        Args:
            custom_prompt: Optional custom prompt to use instead of default.

        Returns:
            Formatted system prompt string.

        """
        try:
            if custom_prompt:
                logger.debug("Using custom system prompt")
                return custom_prompt

            max_len = self.config.commit.max_line_length
            logger.debug(f"Building system prompt with max_line_length={max_len}")

            # Make sure DEFAULT_SYSTEM_PROMPT is defined and has the correct format
            if not globals().get("DEFAULT_SYSTEM_PROMPT"):
                logger.error("DEFAULT_SYSTEM_PROMPT is not defined")
                raise ValueError("DEFAULT_SYSTEM_PROMPT is not defined")

            prompt = DEFAULT_SYSTEM_PROMPT.format(max_line_length=max_len)

            if not prompt or not prompt.strip():
                logger.error("Generated system prompt is empty")
                raise ValueError("Generated system prompt is empty")

            logger.debug(f"System prompt length: {len(prompt)} characters")
            logger.debug(
                f"System prompt preview: {prompt[:200]}..."
                if len(prompt) > 200
                else f"System prompt: {prompt}"
            )

            return prompt
        except Exception as e:
            logger.error(f"Error building system prompt: {str(e)}", exc_info=True)
            raise

    async def generate_commit_message(
        self,
        diff: str,
        ticket: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a commit message for the given diff.

        Args:
            diff: The git diff to analyze.
            ticket: Optional ticket number (e.g., "AB-1234").
            context: Additional context for the AI (e.g., branch name, related issues).

        Returns:
            Generated commit message.

        Raises:
            ValueError: If the diff is empty or invalid.
            RuntimeError: If the AI fails to generate a message.

        """
        if not diff or not diff.strip():
            raise ValueError("Diff cannot be empty")

        context = context or {}
        user_prompt = self._build_user_prompt(diff, ticket, context)

        try:
            # Debug logging
            logger.debug(f"System prompt: {self.system_prompt}")
            logger.debug(f"User prompt: {user_prompt}")

            if not self.system_prompt or not user_prompt:
                error_msg = f"Empty prompt detected. System prompt: {bool(self.system_prompt)}, User prompt: {bool(user_prompt)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Prepare the messages for the AI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Debug log the messages being sent to the AI
            logger.debug("Sending the following messages to AI:")
            for i, msg in enumerate(messages):
                logger.debug(f"Message {i+1} (role: {msg['role']}):")
                logger.debug(f"{msg['content']}")
                logger.debug("-" * 50)

            # Prepare the initial messages with system prompt
            messages = [{"role": "system", "content": self.system_prompt}]

            # Split the user prompt into chunks if it's too large
            max_chunk_size = 20000  # Keep chunks under 20k characters
            if len(user_prompt) > max_chunk_size:
                logger.warning(
                    f"User prompt is large ({len(user_prompt)} chars), splitting into chunks..."
                )
                chunks = [
                    user_prompt[i : i + max_chunk_size]
                    for i in range(0, len(user_prompt), max_chunk_size)
                ]

                # Add each chunk as a separate user message
                for i, chunk in enumerate(chunks, 1):
                    messages.append(
                        {
                            "role": "user",
                            "content": f"[Part {i}/{len(chunks)}] Here's a chunk of the git diff. Please wait for all parts before analyzing.\n\n{chunk}",
                        }
                    )

                # Add a final message to process all chunks
                messages.append(
                    {
                        "role": "user",
                        "content": "I've sent all parts of the git diff. Please analyze the complete diff and generate a commit message.",
                    }
                )
            else:
                # If the prompt is small enough, just add it as a single message
                messages.append({"role": "user", "content": user_prompt})

            # Debug log the messages being sent to the AI
            logger.debug(f"Prepared {len(messages)} messages for AI")
            for i, msg in enumerate(messages):
                logger.debug(
                    f"Message {i+1} (role: {msg['role']}): {len(msg['content'])} chars"
                )
                if i > 0:  # Skip full content for system message
                    logger.debug(f"Preview: {msg['content'][:200]}...")

            # Log the prompt details
            logger.debug(f"System prompt length: {len(self.system_prompt)}")
            logger.debug(f"User prompt length: {len(user_prompt)}")

            # Call the AI to generate the commit message with Langfuse tracing if enabled
            logger.debug("Calling AI...")
            try:
                if self.config.langfuse.enabled and LANG_FUSE_AVAILABLE and hasattr(self, 'langfuse'):
                    # Create a new trace for this generation
                    trace = self.langfuse.trace(
                        name="generate_commit_message",
                        input={
                            "system_prompt": self.system_prompt[:1000] + "..." if len(self.system_prompt) > 1000 else self.system_prompt,
                            "user_prompt": user_prompt[:1000] + "..." if len(user_prompt) > 1000 else user_prompt,
                            "model_name": self.config.ai.model_name,
                            "temperature": self.config.ai.temperature,
                            "max_tokens": self.config.ai.max_tokens,
                        }
                    )

                    # Create a span for the LLM call
                    generation = trace.generation(
                        name="llm_call",
                        model=self.config.ai.model_name,
                        model_parameters={
                            "temperature": self.config.ai.temperature,
                            "max_tokens": self.config.ai.max_tokens,
                        }
                    )

                    try:
                        response = await self.ai.run(
                            system_prompt=self.system_prompt,
                            user_prompt=user_prompt,
                            output_model=CommitMessageResponse,
                            model_name=self.config.ai.model_name,
                            temperature=self.config.ai.temperature,
                            max_tokens=self.config.ai.max_tokens,
                        )

                        if hasattr(response, 'output') and response.output:
                            output_str = str(response.output)
                            generation.end(
                                output=output_str[:1000] + "..." if len(output_str) > 1000 else output_str
                            )
                        return response

                    except Exception as e:
                        generation.end(error=str(e))
                        raise
                else:
                    # Fallback to standard call if Langfuse is not enabled or available
                    response = await self.ai.run(
                        system_prompt=self.system_prompt,
                        user_prompt=user_prompt,
                        output_model=CommitMessageResponse,
                        model_name=self.config.ai.model_name,
                        temperature=self.config.ai.temperature,
                        max_tokens=self.config.ai.max_tokens,
                    )

                logger.debug("Successfully received response from AI")
            except Exception as e:
                logger.error(f"Error calling AI: {str(e)}")
                logger.error(
                    f"System prompt length: {len(self.system_prompt) if self.system_prompt else 0}"
                )
                logger.error(
                    f"User prompt length: {len(user_prompt) if user_prompt else 0}"
                )
                raise

            if not response or not hasattr(response, "output") or not response.output:
                logger.error(
                    f"No valid response output received from AI. Response: {response}"
                )
                raise ValueError("No valid response output generated by AI")

            # The output is already the commit message string
            if isinstance(response.output, str):
                return response.output.strip()
            else:
                logger.error(f"Unexpected output type: {type(response.output)}")
                raise ValueError("Expected string output from AI")

        except Exception as e:
            logger.error(f"Error generating commit message: {str(e)}")
            raise RuntimeError(f"Failed to generate commit message: {str(e)}") from e

    def _build_user_prompt(
        self, diff: str, ticket: Optional[str], context: Dict[str, Any]
    ) -> str:
        """Build the user prompt for the AI.

        Args:
            diff: The git diff.
            ticket: Optional ticket number.
            context: Additional context.

        Returns:
            Formatted user prompt string.

        """
        try:
            logger.debug(
                f"Building user prompt with diff length: {len(diff)}, ticket: {ticket}"
            )

            if not diff or not diff.strip():
                error_msg = "Diff is empty or contains only whitespace"
                logger.error(error_msg)
                raise ValueError(error_msg)

            prompt_parts = [
                "Please analyze the following git diff and generate a commit message:",
                "",
                "```diff",
                diff.strip(),
                "```",
                "",
            ]

            if ticket:
                logger.debug(f"Including ticket in prompt: {ticket}")
                prompt_parts.extend([f"Ticket: {ticket}", ""])

            if context:
                logger.debug(f"Including context in prompt: {context}")
                if context:  # Only add the header if there's actual context
                    prompt_parts.append("Additional context:")
                    for key, value in context.items():
                        if value is not None:
                            prompt_parts.append(f"- {key}: {value}")
                    prompt_parts.append("")  # Add a blank line after context

            prompt_parts.append(
                "You must generate a commit message ONLY following the specified format and guidelines."
            )

            prompt = "\n".join(prompt_parts)

            # Debug log the final prompt
            logger.debug(f"Built user prompt with length: {len(prompt)}")
            logger.debug(
                f"User prompt preview: {prompt[:300]}..."
                if len(prompt) > 300
                else f"User prompt: {prompt}"
            )

            # Validate the prompt
            if not prompt or not prompt.strip():
                error_msg = "Generated user prompt is empty"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return prompt

        except Exception as e:
            logger.error(f"Error building user prompt: {str(e)}", exc_info=True)
            raise

    @classmethod
    def from_config_file(cls, config_path: str) -> "CommitMessageGenerator":
        """Create a generator from a configuration file.

        Args:
            config_path: Path to the configuration file (JSON or YAML).

        Returns:
            Configured CommitMessageGenerator instance.
        """
        from commit_message_generator.config import load_config_from_file

        try:
            config = load_config_from_file(config_path)

            # Log Langfuse configuration status
            if config and hasattr(config, 'langfuse'):
                if config.langfuse.enabled:
                    if LANG_FUSE_AVAILABLE:
                        logger.info("Langfuse tracing is enabled")
                    else:
                        logger.warning(
                            "Langfuse is enabled in config but langfuse package is not installed. "
                            "Install with: pip install langfuse"
                        )
                else:
                    logger.debug("Langfuse tracing is disabled in config")

            return cls(config=config)

        except Exception as e:
            logger.warning(
                f"Failed to load config from {config_path}, using defaults: {str(e)}"
            )
            return cls()


def generate_commit_message(
    diff: str,
    ticket: Optional[str] = None,
    system_prompt: Optional[str] = None,
    config_path: Optional[str] = None,
) -> str:
    """Generate a commit message from a git diff.

    This is a synchronous wrapper around the async CommitMessageGenerator.

    Args:
        diff: The git diff output
        ticket: Optional ticket number (e.g., "AB-1234")
        system_prompt: Optional custom system prompt
        config_path: Optional path to a configuration file (JSON or YAML)

    Returns:
        Generated commit message as a string

    """
    import asyncio

    # Create the generator with the config file if provided
    if config_path:
        generator = CommitMessageGenerator.from_config_file(config_path)
        # Apply any overrides
        if system_prompt:
            generator.system_prompt = system_prompt
    else:
        generator = CommitMessageGenerator(system_prompt=system_prompt)

    # Run the async generate method in an event loop
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(
            generator.generate_commit_message(diff=diff, ticket=ticket)
        )
    finally:
        # Ensure Langfuse flushes any pending events
        if hasattr(generator, 'langfuse') and generator.langfuse:
            loop.run_until_complete(generator.langfuse.flush())
