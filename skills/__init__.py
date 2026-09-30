"""
Built-in skills for the Trust-First Personal Agent.

Skills in this directory are auto-discovered by core.registry.Registry.load_skills_from_directory().
Use the @skill decorator to expose functions as agent tools.
"""

from core.registry import skill


# Re-export the core tool functions so they can also be loaded dynamically
# if desired, but in practice they are already registered by ToolExecutor.
# Additional custom skills can be added below with the @skill decorator.


@skill(
    name="hello_world",
    description="A minimal demo skill that returns a greeting.",
    schema={
        "name": "hello_world",
        "description": "A minimal demo skill that returns a greeting.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"},
            },
        },
    },
)
def hello_world(name: str = "world") -> str:
    return f"Hello, {name}! This is a custom skill."
