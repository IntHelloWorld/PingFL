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
                "required": ["class_name"],
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
                "required": ["class_name", "method_name"],
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
            "description": "Edit the code of the provided method and run the program to verify the hypotheses.",
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
                                        "Please note that the *SEARCH/REPLACE* edit REQUIRES PROPER INDENTATION. "
                                        "If you would like to search the line '    System.out.println(x);', you must fully write that out, with all those spaces before the code!"
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
2. Return a JSON format results immediately upon identifying a suspicious method. You may continue to call for more functions if initial confidence is low
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

Start by calling the `get_failing_tests_covered_classes` function."
"""


VERIFY_AGENT_EDITOR_SYSTEM_PROMPT = """
You are a software debugging assistant. Given the hypotheses about potential bugs in a method, your task is to verify that if this method is the best repair location using a provided code edit tool (function).

Key Responsibilities:
1. Based on the hypotheses, you should analyze whether the provided method is indeed the location that needs to be fixed by using the `edit_and_run` tool. You may only initiate one function call each time
2. To verify the hypotheses, you may add `System.out.println` statements to observe variable values and make minor changes to the provided method, make sure that the method after edition MUST be compilable and runnable

Special Instructions:
1. If you want to edit multiple places in the provided method, you should initiate only one tool call with multiple *SEARCH/REPLACE* edits as the argument
2. Focus on concrete evidence rather than speculation
"""

VERIFY_AGENT_EDITOR_USER_PROMPT = """
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

The suspicious method looks like:
```java
{method_code}
```

Start verifying the suspicious method by calling the `edit_and_run` function."
"""

VERIFY_AGENT_SYSTEM_PROMPT = """
You are a software debugging assistant. Your task is to verify the hypotheses about potential bugs in a method using a provided code edit tool (function) and finally return the verification result.

Key Responsibilities:
1. Based on the hypotheses, you should continuously analyze whether the provided method is indeed the location that needs to be fixed by using the `edit_and_run` tool, you may only initiate one function call each time
2. To verify the hypotheses, you may add `System.out.println` statements to observe variable values and make minor changes to existing code, make sure that the code after edition MUST be compilable and runnable
3. The tool will return the program output of the modified code, which you need to analyze and decide whether you need to continue calling the editing tool. The tool must not be called more than 3 times.
4. Once you have obtained sufficient evidence, return the verification results in JSON format

Result Formation:
After the verification process is complete, immediately return a JSON result wrapped with ```json...``` in the following format:
```json
{
    "is_buggy": "<true/false>",
    "explanation": "<if the method is buggy, provide a detailed explanation of the bug, otherwise explain why the method is not buggy and provide guidance for the subsequent debugging process>",
}
```

Special Instructions:
1. If you want to edit multiple places in the provided method, you should initiate only one tool call with multiple *SEARCH/REPLACE* edits as the argument
2. Fully consider the data flow and calling relationship between methods, the provided method is verified as buggy only if it is the best place to fix the bug
3. Return a JSON format results immediately upon verifying the method as buggy. You may continue to edit the method if initial confidence is low. The tool must not be called more than 3 times
4. Focus on concrete evidence rather than speculation
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

The suspicious method looks like:
```java
{method_code}
```

Start verifying the suspicious method by calling the `edit_and_run` function."
"""