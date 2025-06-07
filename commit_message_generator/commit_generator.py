"""Commit message generator implementation using Pydantic AI with logfire/langfuse
integration."""

import logging
from pathlib import Path
from typing import List, Optional

from pydantic_ai import Agent

from commit_message_generator.agent_prompts import ERROR_CORRECT_FORMAT, SYSTEM_PROMPT
from commit_message_generator.config import GeneratorConfig
from commit_message_generator.configure_langfuse import configure_langfuse
from commit_message_generator.models import CommitMessageResponse

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

    async def call_ai(self, user_prompt: str, errors: List[str], attempt: int):
        # Compile prompt with any errors
        compiled_prompt = user_prompt + (
            "\n\nErrors:\n" + "\n".join(errors) if errors else ""
        )

        logger.info(f"Compiled prompt length: {len(compiled_prompt)}")

        if self.config.langfuse.enabled:
            with self.tracer.start_as_current_span(
                f"Git-Commit-Message-Generation (attempt {attempt + 1}/{self.config.ai.max_attempts})"
            ) as main_span:
                repo_name = Path.cwd().name
                main_span.set_attribute("langfuse.user.id", f"gcmg-model-{repo_name}")
                main_span.set_attribute(
                    "langfuse.session.id", f"gcmg-session-{self.config.ai.model_name}"
                )
                main_span.set_attribute("input.value", compiled_prompt)

                # Make the AI call with the message history
                response = await self.ai.run(
                    user_prompt=compiled_prompt,
                    output_model=CommitMessageResponse,
                    model=self.config.ai.model_name,
                    temperature=self.config.ai.temperature,
                    max_tokens=self.config.ai.max_tokens,
                )

                main_span.set_attribute("output.value", response.output)
                return response.output
        else:
            # Make the AI call without tracing
            response = await self.ai.run(
                user_prompt=compiled_prompt,
                output_model=CommitMessageResponse,
                model=self.config.ai.model_name,
                temperature=self.config.ai.temperature,
                max_tokens=self.config.ai.max_tokens,
            )
            return response.output

    def _init_ai(self) -> Agent:
        """Initialize the AI client with configuration."""

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

            # Initialize the AI agent with explicit API key and system prompt
            agent = Agent(
                model=ai_config.model_name,
                temperature=ai_config.temperature,
                max_tokens=ai_config.max_tokens,
                top_p=ai_config.top_p,
                api_key=api_key,  # Explicitly pass the API key
                system_prompt=self.system_prompt,  # Include the system prompt
            )

            logger.debug("AI agent initialized successfully")
            return agent

        except Exception as e:
            logger.error(f"Failed to initialize AI agent: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to initialize AI agent: {str(e)}") from e

    def _build_system_prompt(self) -> str:
        """Build the system prompt with configuration values."""

        try:
            if not SYSTEM_PROMPT or not SYSTEM_PROMPT.strip():
                logger.error("System prompt is empty")
                raise ValueError("System prompt is empty")

            formatted_system_prompt = SYSTEM_PROMPT.format(
                first_line_limit=self.config.commit.max_line_length - 20,
                wrap_limit=self.config.commit.max_line_length,
            )
            logger.debug(
                f"System prompt format:\nfirst_line_limit: {self.config.commit.max_line_length - 20}\nwrap_limit: {self.config.commit.max_line_length}"
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

        user_prompt = self._build_user_prompt(diff, ticket)

        try:
            # Debug logging
            logger.debug(f"User prompt: {user_prompt}")

            if not user_prompt:
                error_msg = "Empty user prompt detected"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Call the AI to generate the commit message with retry logic for format validation
            logger.debug("Calling AI...")
            response = None
            max_attempts = self.config.ai.max_attempts
            attempt = 0
            while attempt < max_attempts:
                errors = []
                try:
                    response = await self.call_ai(user_prompt, errors, attempt)

                    # Single point of response validation
                    if not response:
                        error_msg = "No valid response output received from AI"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(error_msg)
                        attempt += 1
                        continue

                    # Validate response format
                    lines = response.split("\n")
                    first_line = lines[0]
                    empty_line = lines[1] if len(lines) > 1 else ""
                    description = lines[2:] if len(lines) > 2 else []
                    prefix = first_line.split(":")[0]
                    commit_type = prefix.split("/")[0]
                    severity = prefix.split("/")[1]
                    ticket_number = first_line.split(":")[1].split(" - ")[0]

                    logger.info(f"First line: {first_line}")
                    logger.info(f"Prefix: {prefix}")
                    logger.info(f"Commit type: {commit_type}")
                    logger.info(f"Severity: {severity}")
                    logger.info(f"Ticket number: {ticket_number}")

                    # Check if response starts with code block (Prohibited in system instructions)
                    if first_line.startswith("```"):
                        error_msg = "[ERROR] Response starts with code block while it should not!"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check if prefix exists
                    if not prefix:
                        error_msg = (
                            "[ERROR] Commit title (first line) prefix does not exist!"
                        )
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check if prefix is correctly formatted
                    if not commit_type or not severity:
                        error_msg = "[ERROR] Commit title (first line) prefix is not correctly formatted!"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check if ticket number matches
                    if ticket.strip() != ticket_number.strip():
                        error_msg = "[ERROR] Ticket number does not match the one from the User Prompt!"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check if empty_line is correctly set
                    if empty_line.strip() != "":
                        error_msg = "[ERROR] Empty line does not exist!"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check if description is correctly set
                    if len(description) == 0:
                        error_msg = "[ERROR] Description does not exist!"
                        logger.warning(
                            f"{error_msg} (attempt {attempt + 1}/{max_attempts})"
                        )
                        errors.append(
                            error_msg + "\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT
                        )

                    # Check every line of description if it overflow max_line_length
                    for i, line in enumerate(description):
                        if len(line.strip()) > self.config.commit.max_line_length:
                            error_msg = f"[ERROR] detailed_description line {i} overflow max_line_length!"
                            logger.warning(
                                f"{error_msg} (attempt {attempt + 1}/{max_attempts} - {len(line.strip())} > {self.config.commit.max_line_length})"
                            )
                            errors.append(
                                error_msg
                                + "\nFormat **must** be:\n"
                                + ERROR_CORRECT_FORMAT
                            )

                    # --------- If we have errors, try again ---------
                    if errors:
                        logger.warning(
                            f"Commit message format validation failed (attempt {attempt + 1}/{max_attempts})"
                        )
                        attempt += 1
                        continue

                    # If we got here, the format is valid
                    break

                except Exception as e:
                    error_msg = f"AI call failed: {str(e)}"
                    logger.error(f"{error_msg} (attempt {attempt + 1}/{max_attempts})")

                    errors.append("\nFormat **must** be:\n" + ERROR_CORRECT_FORMAT)

                    attempt += 1
                    if attempt >= max_attempts:
                        raise

            # Final validation after all attempts
            if not response or attempt >= max_attempts:
                error_msg = (
                    f"Failed to get valid response after {max_attempts} attempts"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating commit message: {str(e)}")
            raise RuntimeError(f"Failed to generate commit message: {str(e)}") from e

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
