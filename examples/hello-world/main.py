"""
Hello World Plugin - Simple example plugin for Nadoo

This plugin demonstrates the basic structure and features of a Nadoo plugin.
"""

from nadoo_plugin import NadooPlugin, tool, parameter, validator


class HelloWorldPlugin(NadooPlugin):
    """
    Simple hello world plugin demonstrating basic functionality

    Features:
    - Basic greeting tool
    - Parameter validation
    - Context usage (logging)
    """

    def __init__(self):
        super().__init__()

    @tool(name="greet", description="Generate a greeting message for a user")
    @parameter("name", type="string", required=True, description="Name of the person to greet")
    @parameter("language", type="string", required=False, default="english", description="Language for greeting (english, spanish, french, korean)")
    @validator("language", allowed_values=["english", "spanish", "french", "korean"])
    def greet(self, name: str, language: str = "english") -> dict:
        """
        Generate a greeting in the specified language

        Args:
            name: Name to greet
            language: Language for greeting

        Returns:
            dict with greeting message
        """
        self.context.info(f"Generating greeting for {name} in {language}")

        # Define greetings
        greetings = {
            "english": f"Hello, {name}! Welcome to Nadoo!",
            "spanish": f"¡Hola, {name}! ¡Bienvenido a Nadoo!",
            "french": f"Bonjour, {name}! Bienvenue à Nadoo!",
            "korean": f"안녕하세요, {name}님! Nadoo에 오신 것을 환영합니다!",
        }

        greeting = greetings.get(language, greetings["english"])

        self.context.trace("greeting_generated", {"name": name, "language": language})

        return {
            "success": True,
            "greeting": greeting,
            "language": language,
            "name": name,
        }

    @tool(name="echo", description="Echo back the input text with optional transformations")
    @parameter("text", type="string", required=True, description="Text to echo")
    @parameter("transform", type="string", required=False, default="none", description="Transformation to apply (none, uppercase, lowercase, reverse)")
    @validator("transform", allowed_values=["none", "uppercase", "lowercase", "reverse"])
    @validator("text", min_length=1, max_length=1000)
    def echo(self, text: str, transform: str = "none") -> dict:
        """
        Echo text with optional transformation

        Args:
            text: Text to echo
            transform: Transformation type

        Returns:
            dict with echoed text
        """
        self.context.info(f"Echoing text with transform: {transform}")
        self.context.watch_variable("original_text", text)

        # Apply transformation
        if transform == "uppercase":
            result = text.upper()
        elif transform == "lowercase":
            result = text.lower()
        elif transform == "reverse":
            result = text[::-1]
        else:
            result = text

        self.context.watch_variable("transformed_text", result)
        self.context.trace("text_transformed", {"transform": transform, "length": len(result)})

        return {
            "success": True,
            "original": text,
            "result": result,
            "transform": transform,
        }

    @tool(name="add_numbers", description="Add two numbers together")
    @parameter("a", type="number", required=True, description="First number")
    @parameter("b", type="number", required=True, description="Second number")
    def add_numbers(self, a: float, b: float) -> dict:
        """
        Add two numbers

        Args:
            a: First number
            b: Second number

        Returns:
            dict with sum
        """
        self.context.info(f"Adding {a} + {b}")

        result = a + b

        self.context.watch_variable("result", result)
        self.context.trace("calculation_completed", {"operation": "addition"})

        return {
            "success": True,
            "a": a,
            "b": b,
            "sum": result,
        }


# Export plugin instance
plugin = HelloWorldPlugin()
