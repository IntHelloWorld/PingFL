SEARCH_AGENT_TOOLS = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_covered_classes",
    #         "description": "Get a dictionary of all source classes and test classes covered by the failing test.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {},
    #             "required": [],
    #             "additionalProperties": False
    #         }
    #     }
    # },
    {
        "type": "function",
        "function": {
            "name": "get_covered_methods_of_class",
            "description": "Get a list of all covered methods of a class. Support precise and fuzzy matches for class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A text to describe your analysis and the reason for the tool call."
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input a partial class name such as 'MyClass'."
                    }
                },
                "required": ["thought", "class_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code",
            "description": "Get the code of the covered method(s) from a specified class. Support precise and fuzzy matches for class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A text to describe your analysis and the reason for the tool call."
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input a partial class name such as 'MyClass'."
                    },
                    "method_name": {
                        "type": "string",
                        "description": "The method name. Directly input the method name such as 'myMethod'."
                    }
                },
                "required": ["thought", "class_name", "method_name"],
                "additionalProperties": False
            }
        }
    }
]



VERIFY_AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "edit_and_run",
            "description": "Edit the suspicious method code and run the program to verify the hypotheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A text to describe your thought and the reason for the tool call."
                    },
                    "edits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "edit": {
                                    "type": "string",
                                    "description": (
                                        "Every *SEARCH/REPLACE* edit must use this format:\n"
                                        "1. The start of search block: <<<<<<< SEARCH\n"
                                        "2. A contiguous chunk of lines to search for in the existing source code\n"
                                        "3. The dividing line: =======\n"
                                        "4. The lines to replace into the source code\n"
                                        "5. The end of the replace block: >>>>>>> REPLACE\n\n"
                                        "Here is an example:\n\n"
                                        "<<<<<<< SEARCH\n"
                                        "import com.example.MyClass;\n"
                                        "=======\n"
                                        "import com.example.MyClass;\n"
                                        "import com.example.MyAnotherClass;\n"
                                        ">>>>>> REPLACE\n"
                                    )
                                },
                            },
                            "required": ["edit"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["edits"],
                "additionalProperties": False
            }
        }
    }
]


SEARCH_AGENT_SYSTEM_PROMPT = """
You are an automatic debug agent designed to analyze test failures and identify suspicious methods in software projects. Your goal is to systematically investigate the codebase using provided tools (functions) and finally identify the suspicious method.

Key Responsibilities:
1. Continuously analyze test failures using available function calls, you may initiate parallel function calls
2. Identify suspicious methods that may be causing the failures
3. Provide detailed error analysis and the id of the suspicious method in a structured JSON format

Investigation Protocol:
1. The `get_covered_classes` function will be called by default at the beginning to obtain all classes involved in the failing test
2. You can call the `get_covered_methods_of_class` function to list all covered methods in a class that could potentially contribute to the failure
3. You can call the `get_method_code` function to examine the implementation of a suspicious method

Result Formation:
When a suspicious method is identified, immediately return a JSON result wrapped with ```json...``` in the following format:
```json
{
    "error_analysis": "<detailed explanation of why this method is suspicious>",
    "suspicious_method": "<the method id, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'>",
}
```

Special Instructions:
1. When multiple methods or classes require investigation, you may initiate parallel function calls
2. Return a JSON format results and stop initiating new function calls when you identifying a suspicious method with high confidence
3. Analyze method dependencies and data flow, and consider the inheritance relationship of the class
4. Focus on concrete evidence rather than speculation
"""

SEARCH_AGENT_USER_PROMPT = """
The test `{test_name}` failed.
The test looks like:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```

{experience}Start by calling the `get_failing_tests_covered_classes` function."
"""

EXPERIENCE_PROMPT = """
The previous debugging process provided the following experience:
```
{experience}
```
"""

VERIFY_AGENT_SYSTEM_PROMPT = """
You are a **Software Debugging Assistant**. Your sole responsibility is to **verify hypotheses** about whether a given method contains a bug **based on concrete evidence**, **not to fix the method**. You will do this by observing variable values, inspecting the code's behavior, and reasoning logically.

## Key Instructions:
1. **Verification, not fixing**: Your only objective is to determine whether the provided method is the best location to address the issue. **Do not focus on fixing or improving the code beyond what is strictly necessary for verification**.
2. **Iterative Hypothesis Testing**:
   - Treat any assumption about the bug as a **hypothesis** to test.
   - Use the `edit_and_run` tool to make minimal changes: for example, adding debugging output (`System.out.println`) or making other small modifications to trace execution and variable values.
   - Do not attempt to rewrite or refactor the method unless it's strictly necessary for debugging and testing your hypothesis.
3. **Evidence First, Judgment Later**: Before concluding whether the method is buggy, gather sufficient evidence to confirm or reject all related hypotheses. Your decision must be backed by the outputs or observations of the modified code.
4. **Minimal Tool Use**: Always use the fewest possible modifications to achieve clarity in verification. Save more complex edits for later and only if strictly needed.
5. **Focus on Data Flow and Interactions**: Ensure that you're verifying why this method, and **not a different method**, is the ideal location to address the issue. Consider the context of surrounding methods or the program calls when making your judgment.

## Tool Behavior:
- Use the `edit_and_run` tool to modify and evaluate the code. You must craft the argument to the tool such that the edits are **syntactically and semantically valid** (the tool will only execute compilable and runnable code).
- Each tool invocation must achieve one clear goal, e.g., testing a hypothesis by adding print statements or adjusting specific behaviors for test evaluation. 

## JSON Result Format:
After the verification process is complete, return a JSON object immediately in the following form:
```json
{
    "is_buggy": "<true/false>",
    "explanation": "<if buggy, provide detailed evidence and reasoning about the bug. If not buggy, explain why and provide guidance for further debugging.>"
}
```

## Special Notes:
- **No direct fixes**: Do not attempt to fix the method without first verifying its nature as buggy. Remember, fixing is the responsibility of the programmer using your feedback.
- If multiple edits are required for testing (e.g., multiple print statements), they must be included in **one `edit_and_run` call**.
- Once confident, stop editing and immediately return the JSON result with your conclusion.
- Each function call should be independent, which means that the edits you make in each function call will be applied to the original method code.
"""


VERIFY_AGENT_USER_PROMPT = """
The test `{test_name}` failed.
The test looks like:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```

The hypothesis is that the method `{method_id}` is causing the failure. The reasons are:
```
{hypotheses}
```

Suspicious Method Code:
```java
{method_code}
```

Start verifying the suspicious method by calling the `edit_and_run` function.
"""