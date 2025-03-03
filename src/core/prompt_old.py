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
                                        "2. A contiguous chunk of lines to search for in the existing method code\n"
                                        "3. The dividing line: =======\n"
                                        "4. The lines to replace into the source code\n"
                                        "5. The end of the replace block: >>>>>>> REPLACE\n\n"
                                        "Here is an example:\n\n"
                                        "<<<<<<< SEARCH\n"
                                        "import com.example.MyClass;\n"
                                        "=======\n"
                                        "import com.example.MyClass;\n"
                                        "import com.example.MyAnotherClass;\n"
                                        ">>>>>> REPLACE\n\n"
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
                "required": ["thought", "edits"],
                "additionalProperties": False
            }
        }
    }
]


VERIFY_AGENT_TOOLS_CLAUDE = [
    {
        "name": "edit_and_run",
        "description": "Edit the suspicious method code and run the program.",
        "input_schema": {
            "type": "object",
            "properties": {
                "edited_method": {
                    "type": "string",
                    "description": (
                        "The method code after editing.\n"
                        "For example, if the suspicious method looks like:\n\n"
                        "```java\n"
                        "public int myMethod() {\n"
                        "    int x = 10;\n"
                        "    int y = 20;\n"
                        "    return x + y;\n"
                        "}\n"
                        "```\n\n"
                        "You should return ONLY the edited method code wrapped with ```java...``` such as:\n\n"
                        "```java\n"
                        "public int myMethod() {\n"
                        "    int x = 10;\n"
                        "    int y = 20;\n"
                        "    System.out.println(y);\n"
                        "    return x + y;\n"
                        "}\n"
                    )
                },
            },
            "required": ["edited_method"],
        }
    }
]


VERIFY_AGENT_TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "edit_and_run",
            "description": "Insert print statements in the suspicious method code and run the program. Do not edit more than 50 lines of code at a time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_line": {
                        "type": "integer",
                        "description": "The start line number of the original code that needs to be replaced."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "The end line number of the original code that needs to be replaced."
                    },
                    "replace_code": {
                        "type": "string",
                        "description": (
                            "The code wrapped with ```java...``` to replace the original code with, for example:\n\n"
                            "```java\n"
                            "    try {\n"
                            "        Integer.parseInt(input);\n"
                            "        System.out.println(\"Input is\" + input);\n"
                            "        return true;\n"
                            "    } catch (NumberFormatException e) {\n"
                            "        return false;\n"
                            "```"
                        )
                    },
                },
                "required": ["start_line", "end_line", "replace_code"],
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
You are a Software Debugging Assistant. You will be provided with the test failure information and a java method that was considered suspicious during the previous debugging session. Your task is to verify whether the given method contains the exact location that need to be repaired.

To do this, you need to perform Print Debugging by inserting `System.out.println` statements in the java method. I will run your edited java method and return the text output that the program prints. This Print Debugging process can be repeated multiple times until you have collected enough evidence for the final verification result.

You can insert `System.out.println` statements by returning the edited java method, for example:

We need to check the value of variable 'y'.

```java
public int myMethod() {
    int x = 10;
    int y = 20;
    System.out.println(y);
    return x + y;
}
```

Wrap the edited java method in ```java...```, make sure that the method you provide is complete and can be compiled. DO NOT omit the code content in any form.
IMPORTANT: Please only add `System.out.println` statements for debugging purposes, DO NOT modify the original code logic!

After you have collected enough evidence, you should provide a final verification result in the following JSON format:
```json
{
    "needs_repair": "boolean",  // true if the java method contains the exact location that needs to be repaired, false otherwise
    "explanation": "string",    // Detailed explanation of the verification result
    "suggestion": "string"      // Your suggestion for the subsequent debugging steps, if any
}
```

Special Notes:
1. **Insert Only**: You can only insert `System.out.println` statements for debugging purposes, DO NOT modify the original code logic!
2. **Efficiency**: Try to complete your job in fewer rounds of Print Debugging.
3. **Consider Method Calls**: The current java method DOES NOT contain the location that needs to be fixed if the fault is more likely to be in a callee method.
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