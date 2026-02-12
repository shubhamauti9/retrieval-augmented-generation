from src.text_splitters.base_text_splitter import BaseTextSplitter

"""
Default separator hierarchy
"""
DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

"""
RecursiveCharacterTextSplitter - Smart recursive splitting
The recommended splitter for most use cases. It tries to split
on natural boundaries (paragraphs, sentences, words) recursively
"""
"""
Recursively split text using a hierarchy of separators
This splitter tries to keep semantically related text together
by first trying to split on larger boundaries (paragraphs),
then falling back to smaller ones (sentences, words, characters)
Default separator hierarchy:
    1. "\\n\\n" - Paragraph breaks
    2. "\\n" - Line breaks
    3. " " - Words
    4. "" - Characters

Example:
    >>> splitter = RecursiveCharacterTextSplitter(chunk_size=100)
    >>> text = "Long paragraph...\\n\\nAnother paragraph"
    >>> chunks = splitter.split_text(text)
"""
class RecursiveCharacterTextSplitter(BaseTextSplitter):
    
    """
    Initialize the RecursiveCharacterTextSplitter
    Args:
        separators: List of separators to try, in order
        chunk_size: Target chunk size in characters
        chunk_overlap: Character overlap between chunks
        keep_separator: Whether to keep separators in output
    """
    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        keep_separator: bool = True
    ):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.separators = separators or self.DEFAULT_SEPARATORS
        self.keep_separator = keep_separator
    
    """
    Recursively split text using the separator hierarchy
    Args:
        text: The text to split
    Returns:
        A list of text chunks
    """
    def split_text(self, text: str) -> list[str]:
        return self._split_text(text, self.separators)
    
    """
    Internal recursive splitting method
    Args:
        text: Text to split
        separators: Remaining separators to try
    Returns:
        List of text chunks
    """
    def _split_text(
        self,
        text: str,
        separators: list[str]
    ) -> list[str]:
        final_chunks = []
        
        """
        Find the first separator that exists in the text
        """
        separator = separators[-1]  # Default to last (character split)
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
        
        """
        Split by the chosen separator
        """
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        
        """
        Process each split
        """
        good_splits = []
        
        for split in splits:
            """
            Add separator back if keeping
            """
            if self.keep_separator and separator:
                split_with_sep = split + separator
            else:
                split_with_sep = split
            
            if len(split_with_sep) < self.chunk_size:
                good_splits.append(split_with_sep)
            elif new_separators:
                """
                Recursively split with next separator
                """
                if good_splits:
                    merged = self._merge_splits(good_splits, "")
                    final_chunks.extend(merged)
                    good_splits = []
                
                sub_chunks = self._split_text(split, new_separators)
                final_chunks.extend(sub_chunks)
            else:
                """
                Can't split further, add as is
                """
                if good_splits:
                    merged = self._merge_splits(good_splits, "")
                    final_chunks.extend(merged)
                    good_splits = []
                final_chunks.append(split_with_sep)
        
        """
        Merge remaining good splits
        """
        if good_splits:
            merged = self._merge_splits(good_splits, "")
            final_chunks.extend(merged)
        
        """
        Clean up
        """
        return [chunk.strip() for chunk in final_chunks if chunk.strip()]
