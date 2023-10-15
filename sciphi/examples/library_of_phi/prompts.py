# type: ignore
BOOK_FOREWORD_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the foreward for the book:

#  Title: {title}


To assist you in this task, you have been provided the context bellow:

### Related Context

```
{related_context}
```

Notes:
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for an advanced undergraduate course at MIT.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Begin your response with `## Foreward`

### Response:
"""

BOOK_CHAPTER_INTRODUCTION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing a several paragraph introducton for the chapter shown below (avoid going into too much detail):

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the following context to assist you:

### Related context
```
{related_context}
```

### Recent textbook content
```
{book_context}
```

### Chapter outline
```
{chapter_outline}
```

`

### Response:
"""

BOOK_CHAPTER_BULK_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the chapter and section shown below:

#  Title: {title}

## Chapter: {chapter}

### Section: {section}

### Subsection (optional): {subsection}

To assist you in writing the chapter, you have been provided with some related context and recent chapter contents bellow:

### Related context
```
{related_context}
```

### Recent textbook content
```
{book_context}
```

### Response:
"""

BOOK_CHAPTER_CONCLUSION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are tasked with writing a several paragraph CONCLUSION FOR THE CHAPTER shown below:

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context bellow:

### Related context
```
{related_context}
```

### Recent textbook content
```
{book_context}
```

### Chapter outline
```
{chapter_outline}
```

Following your authoring of the conclusion, write 5 exercises which align with the context of the chapter. Format each with a header `#### Exercise 1` etc.

`

### Response:
"""

# # type: ignore
# BOOK_FOREWORD_PROMPT = """
# ### Instructions:
# You are a writing a book titled "{title}". You are currently writing the foreward for the book:

# #  Title: {title}


# To assist you in this task, you have been provided the context bellow:

# ### Related Context

# ```
# {related_context}
# ```

# Notes:
# - The book is being written in the popular Markdown format.
# - The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for an advanced undergraduate course at MIT.
# - Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
# - Begin your response with `## Foreward`

# ### Response:
# """

# BOOK_CHAPTER_INTRODUCTION_PROMPT = """
# ### Instructions:
# You are a writing a book titled "{title}". You are currently writing a several paragraph introducton for the chapter shown below (avoid going into too much detail):

# #  Title: {title}

# ## Chapter: {chapter}

# To assist you in this task, you have been provided the following context to assist you:

# ### Related context
# ```
# {related_context}
# ```

# ### Recent textbook content
# ```
# {book_context}
# ```

# ### Chapter outline
# ```
# {chapter_outline}
# ```

# `

# ### Response:
# """

# BOOK_CHAPTER_BULK_PROMPT = """
# ### Instructions:
# You are a writing a book titled "{title}". You are currently writing the chapter and section shown below:

# #  Title: {title}

# ## Chapter: {chapter}

# ### Section: {section}

# ### Subsection (optional): {subsection}

# To assist you in writing the chapter, you have been provided with some related context and recent chapter contents bellow:

# ### Related context
# ```
# {related_context}
# ```

# ### Recent textbook content
# ```
# {book_context}
# ```

# ### Response:
# """

# BOOK_CHAPTER_CONCLUSION_PROMPT = """
# ### Instructions:
# You are a writing a book titled "{title}". You are tasked with writing a several paragraph CONCLUSION FOR THE CHAPTER shown below:

# #  Title: {title}

# ## Chapter: {chapter}

# To assist you in this task, you have been provided the context bellow:

# ### Related context
# ```
# {related_context}
# ```

# ### Recent textbook content
# ```
# {book_context}
# ```

# ### Chapter outline
# ```
# {chapter_outline}
# ```

# Following your authoring of the conclusion, write 5 exercises which align with the context of the chapter. Format each with a header `#### Exercise 1` etc.

# `

# ### Response:
# """
