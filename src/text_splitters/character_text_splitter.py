from src.text_splitters.base_text_splitter import BaseTextSplitter

"""
CharacterTextSplitter - Split text by a single separator
The simplest splitting strategy - just split on a character
like newline or period. Good for well-structured text
"""
"""
Split text using a single separator character/string This is the simplest text splitter.
It splits on a single separator (default: double newline for paragraphs) and then
merges small chunks to reach the target size
Attributes:
    separator: The string to split on
Example:
    >>> splitter = CharacterTextSplitter(chunk_size=100, separator="\\n\\n")
    >>> chunks = splitter.split_text("Para 1\\n\\nPara 2\\n\\nPara 3")
    >>> len(chunks)
    1  # Small paragraphs merged into one chunk
"""
class CharacterTextSplitter(BaseTextSplitter):
    
    """
    Initialize the CharacterTextSplitter
    Args:
        separator: String to split on (default: double newline)
        chunk_size: Target chunk size in characters
        chunk_overlap: Character overlap between chunks
        keep_separator: Whether to keep the separator in chunks
    """
    def __init__(
        self,
        separator: str = "\n\n",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        keep_separator: bool = False
    ):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.separator = separator
        self.keep_separator = keep_separator
    
    """
    Split text by the separator and merge into appropriate chunks
    Args:
        text: The text to split
    Returns:
        A list of text chunks
    """
    def split_text(self, text: str) -> list[str]:
        """
        Split text by the separator and merge into appropriate chunks
        Args:
            text: The text to split
        Returns:
            A list of text chunks
        """
        if self.separator:
            splits = text.split(self.separator)
        else:
            splits = list(text)
        
        """
        Add separator back if keeping it
        """
        if self.keep_separator and self.separator:
            splits = [s + self.separator for s in splits[:-1]] + [splits[-1]]
        
        """
        Merge small splits into chunks
        """
        chunks = self._merge_splits(splits, self.separator if not self.keep_separator else "")
        
        """
        Filter empty chunks
        """
        return [chunk.strip() for chunk in chunks if chunk.strip()]
