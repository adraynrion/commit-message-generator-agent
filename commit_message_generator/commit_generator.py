"""Commit message generator implementation using Pydantic AI with logfire/langfuse
integration."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior

from commit_message_generator.agent_prompts import SYSTEM_PROMPT
from commit_message_generator.config import GeneratorConfig
from commit_message_generator.configure_langfuse import configure_langfuse
from commit_message_generator.models import parse_commit_message, CommitMessageResponse


@dataclass
class CommitGeneratorDeps:
    """Dependencies for the commit message generator."""

    repo_name: str = ""


# Configure logging
logger = logging.getLogger(__name__)


class CommitMessageGenerator:
    """AI-powered commit message generator.

    This agent generates commit messages based on git changes and a system prompt. It
    follows the conventional commit format and includes ticket numbers when available.

    """

    def __init__(
        self,
        config: Optional[GeneratorConfig] = None,
    ) -> None:
        """Initialize the commit message generator.

        Args:
            config: Configuration for the generator. If None, default config is used.

        """
        self.config = config or GeneratorConfig()
        self.system_prompt = self._build_system_prompt()
        self.ai = self._init_ai()
        if self.config.langfuse.enabled:
            self.tracer = configure_langfuse(
                langfuse_public_key=self.config.langfuse.public_key,
                langfuse_secret_key=self.config.langfuse.secret_key,
                langfuse_host=self.config.langfuse.host,
            )

    async def call_ai(self, prompt: str) -> Any:
        """Call the AI with the given prompt.

        Args:
            prompt: The prompt to send to the AI.

        Returns:
            The AI's response.

        Raises:
            ValueError: If there's an error calling the AI or if the response is invalid.
        """
        try:
            logger.debug(f"Calling AI with prompt length: {len(prompt)}")

            async def run_ai():
                if self.config.langfuse.enabled:
                    with self.tracer.start_as_current_span(
                        "Git-Commit-Message-Generation"
                    ) as main_span:
                        main_span.set_attribute(
                            "langfuse.user.id", f"gcmg-repo-{self._repo_name}"
                        )
                        main_span.set_attribute(
                            "langfuse.session.id", f"gcmg-model-{self._model_name}"
                        )
                        main_span.set_attribute("input.value", prompt)

                        # Make the AI call with the message history
                        response = await self.ai.run(
                            prompt,
                            output_type=CommitMessageResponse,
                        )

                        if hasattr(response, "output"):
                            main_span.set_attribute("output.value", str(response.output))
                            logger.debug("AI call completed successfully")
                            return response.output

                        return response

                # Fallback without Langfuse
                response = await self.ai.run(
                    prompt,
                    output_type=CommitMessageResponse,
                )

                # Return the output if available, otherwise return the full response
                return response.output if hasattr(response, "output") else response

            return await run_ai()

        except UnexpectedModelBehavior as e:
            error_msg = "The AI model encountered an error while running."
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"AI model error: {str(e)}", exc_info=True)
            else:
                logger.error(error_msg)
            raise ValueError(error_msg) from None

        except Exception as e:
            error_msg = f"Error calling AI: {str(e)}"
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(error_msg, exc_info=True)
            else:
                logger.error("Failed to generate commit message")
            raise ValueError("Failed to generate commit message. Please try again later.") from None

    def _init_ai(self) -> Agent:
        """Initialize the AI agent with the specified configuration.

        Returns:
            Agent: The initialized AI agent

        Raises:
            RuntimeError: If the AI agent cannot be initialized

        """
        try:
            ai_config = self.config.ai
            logger.debug(f"Initializing AI with config: {ai_config}")

            # Get the API key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                error_msg = "OPENAI_API_KEY environment variable is not set"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Using model: {ai_config.model_name}")

            # Get repository name for tracing
            try:
                repo_name = Path.cwd().name
            except Exception:
                repo_name = "unknown"

            # Store metadata as instance variables since Agent doesn't support metadata parameter
            self._repo_name = repo_name
            self._model_name = ai_config.model_name
            self._max_attempts = ai_config.max_attempts

            # Initialize the AI agent with the specified model and parameters
            agent = Agent(  # type: ignore
                model=ai_config.model_name,
                temperature=ai_config.temperature,
                max_tokens=ai_config.max_tokens,
                top_p=ai_config.top_p,
                api_key=api_key,
                system_prompt=self.system_prompt,
                retries=ai_config.max_attempts,
                output_retries=ai_config.max_attempts,
            )

            logger.info("AI agent initialized successfully")
            return agent

        except Exception as e:
            error_msg = f"Failed to initialize AI agent: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def _build_system_prompt(self) -> str:
        """Build the system prompt with configuration values."""

        try:
            if not SYSTEM_PROMPT or not SYSTEM_PROMPT.strip():
                logger.error("System prompt is empty")
                raise ValueError("System prompt is empty")

            formatted_system_prompt = SYSTEM_PROMPT.format(
                wrap_limit=self.config.commit.max_line_length,
            )
            logger.debug(
                f"System prompt wrap_limit: {self.config.commit.max_line_length}"
            )

            return formatted_system_prompt
        except Exception as e:
            logger.error(f"Error building system prompt: {str(e)}", exc_info=True)
            raise

    async def generate_commit_message(
        self,
        diff: str,
        ticket: Optional[str] = None,
    ) -> str:
        """Generate a commit message based on the provided diff and optional ticket.

        Args:
            diff: The git diff to analyze
            ticket: Optional ticket number to include in the commit message

        Returns:
            The generated commit message

        Raises:
            ValueError: If the commit message cannot be generated
            RuntimeError: If there's an error during the generation process

        """
        try:
            logger.debug("Building user prompt")
            user_prompt = self._build_user_prompt(diff, ticket)

            logger.debug("Calling AI to generate commit message")
            response = await self.call_ai(user_prompt)

            if not response or not hasattr(response, "message"):
                error_msg = "The AI did not return a valid commit message. Please try again."
                logger.error(error_msg)
                raise ValueError(error_msg)

            commit_message = response.message.strip()

            # Validate the commit message format
            try:
                # This will raise a ValueError if the message format is invalid
                parse_commit_message(commit_message)
            except ValueError as e:
                error_msg = f"Invalid commit message format: {str(e)}. Please ensure the message follows the required format."
                logger.error(error_msg)
                raise ValueError(error_msg) from e

            logger.info("Successfully generated commit message")
            return commit_message

        except ValueError as e:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            if isinstance(e, UnexpectedModelBehavior):
                error_msg = "The AI model encountered an error while generating the commit message."
            else:
                error_msg = "Failed to generate commit message due to an unexpected error."

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Error details: {str(e)}", exc_info=True)
            else:
                logger.error(error_msg)

            raise ValueError(error_msg) from None  # Suppress the exception chain

    def _build_user_prompt(self, diff: str, ticket: Optional[str]) -> str:
        """Build the user prompt for the AI.

        Args:
            diff: The git diff.
            ticket: Optional ticket number.

        Returns:
            Formatted user prompt string.

        """
        try:
            logger.info(
                f"Building user prompt with diff length: {len(diff)}, ticket: {ticket}"
            )

            if not diff or not diff.strip():
                error_msg = "Diff is empty or contains only whitespace"
                logger.error(error_msg)
                raise ValueError(error_msg)

            prompt_parts = []

            if not ticket:
                error_msg = "Ticket number is missing"
                logger.error(error_msg)
                raise ValueError(error_msg)

            prompt_parts = [
                "Please analyze the following git diff and generate a commit message:",
                "",
                f"ticket_number: {ticket}",
                "",
                "<code_changes>",
                diff.strip(),
                "</code_changes>",
                "",
                "You must generate a commit message ONLY following the specified format and guidelines from your system prompt!",
            ]

            prompt = "\n".join(prompt_parts)

            # Debug log the final prompt
            logger.info(f"Built user prompt with length: {len(prompt)}")
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
