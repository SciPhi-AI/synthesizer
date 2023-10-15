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

To assist you in this task, you have been provided the context which will be covered in this chapter:

### Chapter section topics covered:
```
{book_context}
```

Notes:
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Include the chapter title at the top of your output, formatted as  `## Chapter: [Title]`,  `### Introduction` below that.
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

### Related Context

```
{related_context}
```

### Last textbook section content

```
{book_context}
```

Notes:
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a tone and level of complexity that is appropriate for an advanced undergraduate course at MIT.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- If starting a new section, include `### [Section Title]`
- If starting a new subsection, include `#### [Subsection Title]`
`

### Response:
"""

BOOK_CHAPTER_CONCLUSION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are tasked with writing a several paragraph CONCLUSION FOR THE CHAPTER shown below:

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context bellow:

### Previously written chapter:
```
{book_context}
```

Following your authoring of the conclusion, write 5 exercises which align with the context of the chapter. Format each with a header `#### Exercise 1` etc.

Notes:
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$`
- Start the conclusion the Chapter with a header that reads `### Conclusion`, start the exercises with a header that reads `### Exercises`.

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
