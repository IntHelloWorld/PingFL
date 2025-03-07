STOP_TAG = "<STOP_DEBUGGING>"

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
                        "description": "A text to describe your analysis and the reason for the tool call.",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "The class name. For precise matches, input the full class name such as 'com.example.MyClass'. For fuzzy matches, input a partial class name such as 'MyClass'.",
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
            "name": "get_method_code",
            "description": "Get the code of the method(s) from a specified class. Support precise and fuzzy matches for class name.",
            "parameters": {
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
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_methods_contain_string",
            "description": "Get a list of all production methods containing a specific string content. This tool can be used to search for methods responsible for printing test output strings or to statically find caller/callee methods by method name.",
            "parameters": {
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
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_caller_methods",
            "description": "Get a list of covered method IDs that have called the specified method during runtime.",
            "parameters": {
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
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_callee_methods",
            "description": "Get a list of covered method IDs that have been called by the specified method during runtime.",
            "parameters": {
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
                "additionalProperties": False,
            },
        },
    },
]


SEARCH_AGENT_DEBUGGING_PROMPT_MULTIPLE = f"""
You are a Software Debugging Assistant. Your objective is to browse the codebase using provided tools (functions) and pinpoint the Java method which is potentially responsible for the test failure.

## Callable Functions
1. **get_covered_methods_of_class**: Obtain a list of all covered methods within a class.
2. **get_method_code**: Obtain the source code of a specific method.
3. **search_methods_contain_string**: Obtain all production methods (both covered and not covered) containing a specific string content. This tool can be used to search for methods responsible for printing test output strings or to statically find caller/callee methods by method name.
4. **get_caller_methods**: Obtain all covered methods that have called the specified method during runtime.
5. **get_callee_methods**: Obtain all covered methods that have been called by the specified method during runtime.

## Action Protocol
1. Analyze the given information and call the callable functions to browse the codebase, note that you can initiate parallel function calls to explore different decision branches simultaneously.
2. Judge whether you have collected enough evidence to pinpoint a suspicious Java method, if not, please continue calling the functions to explore the codebase further.
3. Once you have identified a suspicious method with high confidence, stop calling new functions and provide a debug report.
4. If you feel the current browsing process is unnecessary to continue, you can terminate it early by outputting "{STOP_TAG}" without function calls.

NOTE:
- When multiple methods or classes require investigation, you may initiate parallel function calls.
- Contain your thoughts in the argument for each function call you initiate.
- Focus on concrete evidence rather than speculation.
"""

SEARCH_AGENT_DEBUGGING_PROMPT_SINGLE = f"""
You are a Software Debugging Assistant. Your objective is to browse the codebase using provided tools (functions) and pinpoint the Java method which is potentially responsible for the test failure.

## Callable Functions
1. **get_covered_methods_of_class**: Obtain a list of all covered methods within a class.
2. **get_method_code**: Obtain the source code of a specific method.
3. **search_methods_contain_string**: Obtain all production methods (both covered and not covered) containing a specific string content. This tool can be used to search for methods responsible for printing test output strings or to statically find caller/callee methods by method name.
4. **get_caller_methods**: Obtain all covered methods that have called the specified method during runtime.
5. **get_callee_methods**: Obtain all covered methods that have been called by the specified method during runtime.

## Action Protocol
1. Analyze the given information and call the callable functions to browse the codebase.
2. Judge whether you have collected enough evidence to pinpoint a suspicious Java method, if not, please continue calling the functions to explore the codebase further.
3. Once you have identified a suspicious method with high confidence, stop calling new function and provide a debug report.

NOTE:
- Contain your thoughts in the argument for each function call you initiate.
- Focus on concrete evidence rather than speculation.
"""

SEARCH_AGENT_RESULT_PROMPT_SINGLE = """
Based on the debug report, please provide the most suspicious method in the following JSON format.

```json
{
    "error_analysis": "string",  // Detailed explanation of why this method is suspicious
    "method_id": "string"        // The method id, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'
}
```

NOTE:
1. DO NOT provide a test method as the suspicious method, as we are looking for the production method that may cause the test failure.
2. Wrap the JSON result in the ```json...``` block.
"""

SEARCH_AGENT_RESULT_PROMPT_MULTIPLE = """
Based on the debug report, please provide **UP TO 3** most suspicious methods that needs to be further investigated in the structured JSON format.

Each method should be represented as an object with the following schema:

```json
{
  "type": "object",
  "properties": {
    "error_analysis": {
      "type": "string",
      "description": "Detailed explanation of why this method is suspicious"
    },
    "method_id": {
      "type": "string",
      "description": "The method id, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'"
    }
  }
}
```

Please ensure that:

1. Provide up to 3 most suspicious methods.
2. Each method is unique and contains a valid `method_id` (e.g., `com.example.MyClass.InnerClass.methodName#20-30`).
3. The `error_analysis` field provides a detailed explanation of why the method is considered suspicious (e.g., potential vulnerabilities, bad practices, or anomalous behavior).
4. The output is a JSON array of objects, where each object adheres to the schema above.
5. The output is wrapped with the ```json...``` block.

For example, the output should look like this:

```json
[
  {
    "error_analysis": "This method lacks proper input validation, which may lead to the test failure.",
    "method_id": "com.example.AuthService.login#45-55"
  },
  {
    "error_analysis": "This method contains a potential issue with the data processing logic.",
    "method_id": "com.example.DataProcessor.processData#120-130"
  }
]
```
"""

SEARCH_AGENT_USER_PROMPT = """
# Test Failure Information
The test `{test_name}` failed.
The test looks like:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```

{experience}

Start by calling the `get_failing_tests_covered_classes` function."
"""

EXPERIENCE_PROMPT = """
# Previous Debugging Experience

The following methods were considered not the location to fix the test failure:
```
{benign_methods}
```

The following methods were considered uncertain and require further investigation:
```
{uncertain_methods}
```
"""

SINGLE_EXPERIENCE_PROMPT = """Method ID: {method_id}
Reason: {explanation}
Suggestion: {suggestion}"""


VERIFY_AGENT_DEBUGGING_PROMPT = """
You are a Software Debugging Assistant. You will be provided with the test failure information and a java method that was considered suspicious during the previous debugging session.

Your goal is to performing print debugging on the suspicious Java method to verify that if it is the best location to fix the test failure.

## Print Debugging

You should inserting `System.out.println` statements into the suspicious Java method by generating A SINGLE *SEARCH/REPLACE* edit each time.

NOTE:
- Explain your reasoning before providing the *SEARCH/REPLACE* edit.
- Wrap the *SEARCH/REPLACE* edit in blocks ```java...```.
- The *SEARCH/REPLACE* edit REQUIRES PROPER INDENTATION. You must fully write the spaces before every code line!
- You can only edit the given suspicious method, DO NOT edit or create other methods.
- Please only add `System.out.println` statements for debugging purposes, DO NOT change the original code functionality!

The *SEARCH/REPLACE* edit must use this format:
1. The start of search block: <<<<<<< SEARCH
2. A contiguous chunk of lines to search for in the existing source code
3. The dividing line: =======
4. The lines to replace into the source code
5. The end of the replace block: >>>>>>> REPLACE

Here is an example:

We need to check the value of variable 'x'.
```java
<<<<<<< SEARCH
    x = y + z;
=======
    x = y + z;
    System.out.println("Value of x: " + x);
>>>>>>> REPLACE
```

## Action Protocol
1. Analyze the given information and generate A SINGLE *SEARCH/REPLACE* edit to purposefully debug the suspicious Java method, focus on a certain part of the logic at a time if the method code is long.
2. Judge whether you have collected enough evidence based on the program output, if not, please **re-edit the suspicious Java method from scratch** by generating a new *SEARCH/REPLACE* edit.
3. You can make up to 5 edits. Once you have collected enough evidence or the maximum number of edits is reached, you should stop generating more edits and provide a debug report.
"""

VERIFY_AGENT_RESULT_PROMPT = """
Based on the debug report, please determine whether the suspicious Java method is the best location to fix the test failure.

You should provide a final verification result in the following JSON format:
```json
{
    "category": "string",      // The category of the verification result. "buggy" denotes the method is very likely to be the best repair position; "benign" denotes the method does not appear to contain locations that require repair; "uncertain" denotes the method may be on the error propagation path and requires further investigation.
    "explanation": "string",   // Detailed explanation of the verification result
    "suggestion": "string"     // Your suggestion for the subsequent debugging steps, if any
}
```

NOTE:
- Wrap the JSON result in the ```json...``` block.
- Focus on concrete evidence rather than speculation.
- Consider method dependencies and data flow, the given method is not the best location if the fault is more likely in a callee method.
"""

VERIFY_AGENT_USER_PROMPT = """
# Test Failure Information:

The test `{test_name}` failed.
The test looks like:
```java
{test_code}
```

It failed with the following error message and call stack:
```
{error_message}
```

Suspicious Method:

The method `{method_id}` was considered suspicious during the previous debugging session. The reasons are:
```
{hypotheses}
```

The method looks like:
```java
{method_code}
```
"""

SUMMARIZE_SYSTEM_PROMPT = """You are a Software Debugging Assistant."""

SUMMARIZE_USER_PROMPT = """
The previous debugging process found the Java method that may cause the test failure for each failed test case. Now, given the information of each failed test case and its corresponding suspicious method information, please sort all candidate methods in descending order according to their suspicion and provide the user with a sorted list of methods.

# Failed Test Cases and the Corresponding Suspicious Methods

{result_report}

# Result Format

You should provide a method rank list, each method should be in the following JSON format:
```json
{
    "method_id": "string",      // The method id, e.g., 'com.example.MyClass.InnerClass.methodName#20-30'
    "explanation": "string",   // Detailed explanation of why this method is suspicious
}
```

An example of the output:
```json
[
  {
    "method_id": "com.example.AuthService.login#45-55",
    "explanation": "This method lacks proper input validation, which may lead to the test failure."
  },
  {
    "method_id": "com.example.DataProcessor.processData#120-130",
    "explanation": "This method contains a potential issue with the data processing logic."
  }
]

# NOTE
- A method is more suspicious if it is likely to cause more test cases to fail.
- The method rank list should be sorted in descending order according to the suspicion level.
- Wrap your output in the ```json...``` block.

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

Suspicious Method ID: `{method_id}`

Explanation: {explanation}
"""
