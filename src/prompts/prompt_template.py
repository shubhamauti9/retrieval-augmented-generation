import re
from typing import Optional

"""
PromptTemplate - Simple template for composing prompts
Templates allow you to define reusable prompt structures
with placeholders that get filled in at runtime
"""
"""
A template for generating prompts with variable substitution
Uses Python string formatting with {variable} placeholders
Validates that all required variables are provided
Attributes:
    template: The template string with {placeholders}
    input_variables: List of required variable names
Example:
    >>> template = PromptTemplate(
    ...     template="Answer this: {question}\\nContext: {context}",
    ...     input_variables=["question", "context"]
    ... )
    >>> prompt = template.format(question="What is AI?", context="...")
"""
class PromptTemplate:
    
    """
    Initialize the prompt template
    Args:
        template: Template string with {variable} placeholders
        input_variables: List of required variable names
                        If None, auto-detected from template
    """
    def __init__(
        self,
        template: str,
        input_variables: Optional[list[str]] = None
    ):
        self.template = template
        
        if input_variables is None:
            """
            Auto-detect variables from template
            """
            self.input_variables = self._extract_variables(template)
        else:
            self.input_variables = input_variables
    
    """
    Extract variable names from a template string
    Args:
        template: Template string with {variable} placeholders
    Returns:
        List of variable names
    """
    def _extract_variables(self, template: str) -> list[str]:
        """
        Find all {variable_name} patterns
        """
        pattern = r"\{(\w+)\}"
        matches = re.findall(pattern, template)
        """
        Remove duplicates while preserving order
        """
        seen = set()
        return [x for x in matches if not (x in seen or seen.add(x))]
    
    """
    Format the template with provided values
    Args:
        **kwargs: Variable name-value pairs
    Returns:
        The formatted prompt string
    Raises:
        ValueError: If required variables are missing
    """
    def format(self, **kwargs) -> str:
        """
        Check all required variables are provided
        """
        missing = set(self.input_variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        return self.template.format(**kwargs)
    
    """
    Create a new template with some variables pre-filled
    Args:
        **kwargs: Variables to pre-fill
    Returns:
        A new PromptTemplate with remaining variables
    """
    def partial(self, **kwargs) -> "PromptTemplate":
        new_template = self.template
        for key, value in kwargs.items():
            new_template = new_template.replace(f"{{{key}}}", str(value))
        
        remaining_vars = [v for v in self.input_variables if v not in kwargs]
        
        return PromptTemplate(
            template=new_template,
            input_variables=remaining_vars
        )
    
    """
    Return a string representation
    """
    def __repr__(self) -> str:
        preview = self.template[:50] + "..." if len(self.template) > 50 else self.template
        return f"PromptTemplate(template='{preview}', variables={self.input_variables})"
