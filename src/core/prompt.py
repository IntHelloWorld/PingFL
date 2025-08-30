TOOLS_AUTOFL = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The full class name such as 'com.example.MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
]

TOOLS_ENHANCED = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The full class name such as 'com.example.MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_covered_class_full_name",
            "description": "This function returns the possible full class name for a given class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The short class name to search for, e.g., 'MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_covered_method_id",
            "description": "This function returns the possible method IDs for the given method name and class name (optional).",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_name": {
                        "type": "string",
                        "description": "The method name to search for, e.g., 'myMethod'.",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The short class name to search for, e.g., 'MyClass'.",
                    },
                },
                "required": ["method_name"],
                "additionalProperties": False,
            },
        },
    },
]

STOP_TAG = "<STOP_DEBUGGING>"

TOOLS_PRINT_DEBUG = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The full class name such as 'com.example.MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nominate_suspicious_method",
            "description": "This function nominates a suspicious Java method for further investigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The method id of the Java method.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exit_debugging",
            "description": "This function terminates the debugging session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]


TOOLS_PINGFL = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The full class name such as 'com.example.MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nominate_suspicious_method",
            "description": "This function nominates a suspicious Java method for further investigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The method id of the Java method.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exit_debugging",
            "description": "This function terminates the debugging session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_covered_class_full_name",
            "description": "This function returns the possible full class name for a given class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The short class name to search for, e.g., 'MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_covered_method_id",
            "description": "This function returns the possible method IDs for the given method name and class name (optional).",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_name": {
                        "type": "string",
                        "description": "The method name to search for, e.g., 'myMethod'.",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The short class name to search for, e.g., 'MyClass'.",
                    },
                },
                "required": ["method_name"],
                "additionalProperties": False,
            },
        },
    },
]

TOOLS_PINGFL_NO_ENHANCED = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class.",
            "parameters": {
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The full class name such as 'com.example.MyClass'.",
                    },
                },
                "required": ["class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nominate_suspicious_method",
            "description": "This function nominates a suspicious Java method for further investigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method_id": {
                        "type": "string",
                        "description": "The method id of the Java method.",
                    },
                },
                "required": ["method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exit_debugging",
            "description": "This function terminates the debugging session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]

TOOLS_AUTOFL_WITH_THOUGHT = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class. It supports precise and fuzzy matches for class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input the class name such as 'MyClass'.",
                    },
                },
                "required": ["thought", "class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_ids_contain_string",
            "description": "This function returns the IDs of all methods containing a specific string content. It can be used to search for methods responsible for printing specific string or to statically find caller/callee methods by method name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "string_content": {
                        "type": "string",
                        "description": "The string content to search for, requires proper indentation.",
                    },
                },
                "required": ["thought", "string_content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_caller_method_ids",
            "description": "This function returns the IDs of all methods that have called the specified method during runtime.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The method id to search for its callers.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_callee_method_ids",
            "description": "This function returns the IDs of all methods that have been called by the specified method during runtime.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The method id to search for its callees.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
]

SEARCH_AGENT_TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids_for_class",
            "description": "This function returns the IDs of all covered methods in a class. It supports precise and fuzzy matches for class name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input the class name such as 'MyClass'.",
                    },
                },
                "required": ["thought", "class_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_code_for_id",
            "description": "This function returns the source code of the method with the specified method ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The complete method id to search for its code, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_method_ids_contain_string",
            "description": "This function returns the IDs of all methods containing a specific string content. It can be used to search for methods responsible for printing specific string or to statically find caller/callee methods by method name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "string_content": {
                        "type": "string",
                        "description": "The string content to search for, requires proper indentation.",
                    },
                },
                "required": ["thought", "string_content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_caller_method_ids",
            "description": "This function returns the IDs of all methods that have called the specified method during runtime.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The method id to search for its callers.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_callee_method_ids",
            "description": "This function returns the IDs of all methods that have been called by the specified method during runtime.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your analysis and the reason for initiate the function call.",
                    },
                    "method_id": {
                        "type": "string",
                        "description": "The method id to search for its callees.",
                    },
                },
                "required": ["thought", "method_id"],
                "additionalProperties": False,
            },
        },
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "perform_print_debugging_on_method",
    #         "description": "This function performs print debugging on a suspicious Java method to verify if it is really the best location to fix the test failure.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "thought": {
    #                     "type": "string",
    #                     "description": "Your analysis and the reason for initiate the function call.",
    #                 },
    #                 "method_id": {
    #                     "type": "string",
    #                     "description": "The method id of the suspicious method you want to verify.",
    #                 },
    #             },
    #             "required": ["thought", "method_id"],
    #             "additionalProperties": False,
    #         },
    #     },
    # },
]

SEARCH_AGENT_TOOLS_ANTHROPIC = [
    {
        "name": "get_covered_method_ids_for_class",
        "description": "Get a list of all covered methods of a class. Support precise and fuzzy matches for class name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A text to describe your analysis and the reason for the tool call.",
                },
                "class_name": {
                    "type": "string",
                    "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input a partial class name such as 'MyClass'.",
                },
            },
            "required": ["thought", "class_name"],
        },
    },
    {
        "name": "get_method_code_for_id",
        "description": "Get the code of the method(s) from a specified class. Support precise and fuzzy matches for class name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A text to describe your analysis and the reason for the tool call.",
                },
                "class_name": {
                    "type": "string",
                    "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input a partial class name such as 'MyClass'.",
                },
                "method_name": {
                    "type": "string",
                    "description": "The method name. Directly input the method name such as 'myMethod'.",
                },
            },
            "required": ["thought", "class_name", "method_name"],
        },
    },
    {
        "name": "get_method_ids_contain_string",
        "description": "Get a list of all production methods containing a specific string content. This tool can be used to search for methods responsible for printing test output strings or to statically find caller/callee methods by method name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A text to describe your analysis and the reason for the tool call.",
                },
                "string_content": {
                    "type": "string",
                    "description": "The string content to search for, requires proper indentation.",
                },
            },
            "required": ["thought", "string_content"],
        },
    },
    {
        "name": "get_caller_method_ids",
        "description": "Get a list of covered method IDs that have called the specified method during runtime.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A text to describe your analysis and the reason for the tool call.",
                },
                "method_id": {
                    "type": "string",
                    "description": "The method id to search for its callers.",
                },
            },
            "required": ["thought", "method_id"],
        },
    },
    {
        "name": "get_callee_method_ids",
        "description": "Get a list of covered method IDs that have been called by the specified method during runtime.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "A text to describe your analysis and the reason for the tool call.",
                },
                "method_id": {
                    "type": "string",
                    "description": "The method id to search for its callees.",
                },
            },
            "required": ["thought", "method_id"],
        },
    },
]

FAULT_LOCALIZATION_PROMPT_AUTOFL = """Based on the available information, provide the IDs of the most likely culprit Java methods for the bug. Your answer will be processed automatically, so make sure to only answer with the accurate IDs of all likely culprits (e.g., 'com.example.MyClass.InnerClass.methodName#20-30'), without commentary (one per line)."""

FAULT_LOCALIZATION_PROMPT = """Based on the available information, list the most likely culprit Java methods for the bug. Provide each method on a separate line using the following format:

method_id (confidence)

Where:
- method_id should be in the form: package.Class.methodName#lineRange
- confidence is one of:
  high: Strong evidence points to this method
  medium: Some evidence suggests this method
  low: This method is a possible but less likely candidate

Example output:
com.example.MyClass.methodName#20-30 (high)
org.project.Utils.helperMethod#45-60 (medium)

Do not include any additional commentary or explanations."""

REACH_MAX_TOOL_CALLS = """The maximum number of tool calls has been reached, please stop calling new functions and immediately provide a step-by-step explanation of how the bug occurred."""

REACH_MAX_VERIFY_ROUNDS = """The maximum number of verify rounds has been reached, please stop calling new functions and immediately provide a debug report summarizing your debugging process and findings."""

VERIFY_PLAN_SUMMARIZATION_PROMPT = """The following method has been nominated as suspicious: 

Method ID: {method_id}
Reason: {reason}

Given the debugging information so far, please provide a **Verification Plan** to verify if the suspicious method is the best location to fix the test failure. The verification plan should include the following sections:
1. **Issues Identified**: List the potential issues that may cause the test failure.
2. **Suspicious Method Functionality**: Describe the suspicious method's functionality and why it may be causing the test failure.
3. **Verification Goal**: Explain the goal of the verification plan.

Note:
- Since we have not yet determined the actual error location, please use a hypothetical tone.
- DO NOT provide fix suggestions! We aim to verify the suspicious method through print debugging.

Here is a example:
\"\"\"
# Verification Plan

## Issues Identified
The test expects the variable `a` to retain its assignment (`a = err`) and be used in the `return` statement (`return a.stack`). However, the actual result shows `err.stack` being returned, indicating that the inlining logic replaced `a` with `err` directly, bypassing the `catch` block's assignment.

## Suspicious Method Functionality
The `Candidate.canInline#280-411` method contains logic to determine whether a variable can be inlined. Notably, it includes a check for `catch` expressions (commented as \"a direct reference to a catch expression\"). However, the logic seems to reject inlining for certain cases involving `catch` expressions, but the test failure suggests that the inlining is still happening incorrectly.

## Verification Goal
Add print statements to the `Candidate.canInline#280-411` method, checking if it not sufficiently restricting inlining for variables assigned in `catch` blocks.
\"\"\"

Now, please directly provide the verification plan without any additional explanation.
"""

SEARCH_AGENT_USER_PROMPT = """
# Test Failure Information

The test `{test_name}` failed.

The source code of the failing test method is:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```
"""

AUTOFL_DEBUGGING_PROMPT = """
You are a Software Debugging Assistant. You will be provided with the test failure information and a set of callable functions to help you debug the issue. Your task is to provide a step-by-step explanation of how the bug occurred using the provided callable functions.

NOTE:
- You will be given up to 9 rounds to call the functions to gather relevant information.
- After you have gathered enough information, please stop calling new functions and directly provide a step-by-step explanation of how the bug occurred.
"""

PINGFL_SUMMARIZATION_PROMPT = """Based on the available information, provide a step-by-step explanation of how the bug occurred."""

PINGFL_DEBUGGING_PROMPT = """
You are a Software Debugging Assistant. You will be provided with the test failure information and a set of callable functions to help you debug the issue. Your task is to understand the root cause of the bug step-by-step using the callable functions.

NOTE:
- Explain your analysis and thoughts before each function call you initiate.
- You have up to {max_tool_calls} chances to call the functions.
- If you have understood the root cause, call the `exit_debugging` function to terminate the debugging session.
"""

PINGFL_DEBUGGING_PROMPT_NO_THOUGHT = """
You are a Software Debugging Assistant. You will be provided with the test failure information and a set of callable functions to help you debug the issue. Your task is to understand the root cause of the bug step-by-step using the callable functions.

NOTE:
- You have up to {max_tool_calls} chances to call the functions.
- If you have understood the root cause, call the `exit_debugging` function to terminate the debugging session.
"""

PINGFL_DEBUGGING_PROMPT_PARALLEL = """
You are a Software Debugging Assistant. You will be provided with the test failure information and a set of callable functions to help you debug the issue. Your task is to understand the root cause of the bug step-by-step using the callable functions.

NOTE:
- Explain your analysis and thoughts before each function call you initiate.
- You have up to {max_tool_calls} chances to call the functions.
- You can use parallel function calls to explore different perspectives.
- If you have understood the root cause, call the `exit_debugging` function to terminate the debugging session.
"""

REACH_MAX_EDIT_COUNTS = """The maximum number of edit counts has been reached, please stop generating new edit and immediately provide a debug report summarizing your debugging process and findings."""

REACH_MAX_RETRY_COUNTS = """The maximum number of retry counts has been reached, please stop generating new edit and immediately provide a debug report summarizing your debugging process and findings."""

VERIFY_AGENT_DEBUGGING_PROMPT = """
You are a Software Debugging Assistant. You will be provided with the test failure information, the suspicious Java method, and the suspected issue. Your goal is to provide a explanation about whether the suspicious method's functionality matches the suspected issue by performing **Print Debugging**.

## **Print Debugging**

To perform print debugging, you should inserting `System.out.println` statements into the suspicious Java method by generating A SINGLE *SEARCH/REPLACE* edit.

The *SEARCH/REPLACE* edit must use this format:
1. The start of search block: <<<<<<< SEARCH
2. A contiguous chunk of lines to search for in the existing source code
3. The dividing line: =======
4. The lines to replace into the source code
5. The end of the replace block: >>>>>>> REPLACE

Here is an example:

We need to check the value of variable 'x'.
```edit
<<<<<<< SEARCH
    x = y + z;
=======
    x = y + z;
    System.out.println("Value of x: " + x);
>>>>>>> REPLACE
```

NOTE:
- Explain your reasoning before providing the *SEARCH/REPLACE* edit.
- Wrap the *SEARCH/REPLACE* edit in blocks ```edit...```.
- The *SEARCH/REPLACE* edit REQUIRES PROPER INDENTATION. You must fully write the spaces before every code line!
- You can only edit the given suspicious method, DO NOT edit or create other methods.
- Please only add `System.out.println` statements for debugging purposes, DO NOT change the original code functionality!

## Action Protocol
1. Analyze the given information and generate A SINGLE *SEARCH/REPLACE* edit to purposefully debug the suspicious Java method, focus on a certain part of the logic at a time if the method code is long.
2. Judge whether you have collected enough evidence based on the program output, if not, please **re-edit the suspicious Java method from scratch** by generating a new *SEARCH/REPLACE* edit.
3. You can make up to {max_edit_count} edits. Once you have collected enough evidence or the maximum number of edits is reached, you should stop generating more edits and provide a explanation of whether the suspicious method's functionality matches the suspected issue.
"""

VERIFY_AGENT_USER_PROMPT = """
# Test Failure Information:

The test `{test_name}` failed.

The source code of the failing test method is:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```

# Suspicious Method

The method `{method_id}` was considered suspicious during the previous debugging session.

The source code of the suspicious method is:
```java
{method_code}
```

{suspected_issue}
"""

SUMMARIZE_SYSTEM_PROMPT = """You are a Software Debugging Assistant."""

SUMMARIZE_USER_PROMPT = """
Given the information of each failed test case and its corresponding debug report, please sort all suspicious methods in descending order according to their suspicion and provide the user with a sorted list of methods.
Please concentrate on the methods mentioned in the debug report, DO NOT provide irrelevant methods!

# Failed Test Cases and the Corresponding Suspicious Methods

{result_report}

# Result Format

You should provide a method rank list, each method should be in the following JSON format:
```json
{{
    "method_id": "string",      // The method id, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'
    "explanation": "string",   // Detailed explanation of why this method is suspicious
}}
```

An example of the output:
```json
[
  {{
    "method_id": "com.example.AuthService.login#45-55",
    "explanation": "This method lacks proper input validation, which may lead to the test failure."
  }},
  {{
    "method_id": "com.example.DataProcessor.processData#120-130",
    "explanation": "This method contains a potential issue with the data processing logic."
  }}
]

# NOTE
- Concentrate on the methods mentioned in the debug report, DO NOT provide irrelevant methods!
- A method is more suspicious if it is likely to cause more test cases to fail.
- The method rank list should be sorted in descending order according to the suspicion level.
- Wrap your output in the ```json...``` block.
- If no suspicious method is found, please provide an empty list, e.g., ```json\n[]\n```.

Now, please provide the sorted list of methods.
"""

SINGLE_RESULT_TEMPLATE = """
## Debugging Result for Test Case `{test_name}`

Test Code:
```java
{test_code}
```

Error Message:
```
{error_message}
```

Debug Report:
{debug_report}
"""
