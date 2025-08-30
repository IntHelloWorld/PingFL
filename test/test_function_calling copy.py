from openai import OpenAI, base_url
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function

client = OpenAI(
    api_key="sk-xC6z4Safv89vjMQajprgceN3bLDsCWpPprwPvdcKLZviaVFd",
    base_url="https://api.key77qiqi.cn/v1",
)

SEARCH_AGENT_TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "get_covered_method_ids",
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
            "name": "get_method_code_for_id",
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
            "name": "get_method_ids_contain_string",
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
            "name": "get_caller_method_ids",
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
            "name": "get_callee_method_ids",
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

messages = [
    {
        "role": "system",
        "content": "\nYou are a Software Debugging Assistant. Your objective is to pinpoint the Java method which is potentially responsible for the test failure using the following callable functions:\n- **get_covered_method_ids**: Obtain a list of all covered method IDs within a class.\n- **get_method_code_for_id**: Obtain the source code of a specific method.\n- **get_method_ids_contain_string**: Obtain the IDs of all production methods (both covered and not covered) containing a specific string content. This function can be used to search for methods responsible for printing test output strings or to statically find caller/callee methods by method name.\n- **get_caller_method_ids**: Obtain a list of covered method IDs that have called the specified method during runtime.\n- **get_callee_method_ids**: Obtain a list of covered method IDs that have been called by the specified method during runtime.\n\nGiven the debugging context, you will be given up to 15 changes to call the functions to explore the codebase. Once you have identified a suspicious method, please stop calling new functions and immediately provide a debug report summarizing your debugging process and findings.\n\nNOTE:\n- Contain your thoughts in the argument for each function call you initiate.\n- You can refer to previous debugging experience (if provided) to guide your exploration.\n",
    },
    {
        "role": "user",
        "content": '\n# Test Failure Information\nThe test `com.google.javascript.jscomp.TypeCheckTest::testImplementsLoop` failed.\nThe source code of the failing test method is:\n```java\n  public void testImplementsLoop() throws Exception {\n    testClosureTypesMultipleWarnings(\n        suppressMissingProperty("foo") +\n        "/** @constructor \\n * @implements {T} */var T = function() {};" +\n        "alert((new T).foo);",\n        Lists.newArrayList(\n            "Parse error. Cycle detected in inheritance chain of type T"));\n  }\n```\n\nIt failed with the following error message and call stack:\n```\n--- com.google.javascript.jscomp.TypeCheckTest::testImplementsLoop\njunit.framework.AssertionFailedError: expected:<[Parse error. Cycle detected in inheritance chain of type T]> but was:<[can only implement interfaces]>\n\tat com.google.javascript.jscomp.TypeCheckTest.testClosureTypesMultipleWarnings(TypeCheckTest.java:11391)\n\tat com.google.javascript.jscomp.TypeCheckTest.testImplementsLoop(TypeCheckTest.java:9223)\n\n\n```\n\n\n',
    },
    {
        "role": "assistant",
        "content": "First, let's look at all the covered classes to understand the scope:",
    },
    {
        "role": "user",
        "content": 'Covered classes grouped with package name:\n\nCovered source classes:\n{"com.google.javascript.jscomp": ["ComposeWarningsGuard", "SyntacticScopeCreator", "DiagnosticGroupWarningsGuard", "AbstractMessageFormatter", "RhinoErrorReporter", "TypeValidator", "JsAst", "TypeInference", "TypedScopeCreator", "DiagnosticType", "JSError", "BasicErrorManager", "FunctionTypeBuilder", "CheckLevel", "GoogleCodingConvention", "NodeUtil", "MemoizedScopeCreator", "Compiler", "SuppressDocWarningsGuard", "CodingConventions.Proxy", "PrepareAst", "CompilerInput", "DiagnosticGroups", "ProcessClosurePrimitives", "SourceFile", "Scope", "TypeCheck", "LightweightMessageFormatter", "ControlFlowAnalysis", "WarningsGuard", "DiagnosticGroup", "PassFactory", "ControlFlowGraph", "TypeInferencePass", "LoggerErrorManager", "InferJSDocInfo", "CompilerOptions", "ClosureCodingConvention"], "com.google.javascript.jscomp.type": ["ChainableReverseAbstractInterpreter", "ClosureReverseAbstractInterpreter", "SemanticReverseAbstractInterpreter"], "com.google.javascript.jscomp.graph": ["LinkedDirectedGraph", "Graph", "DiGraph"], "com.google.javascript.jscomp.parsing": ["IRFactory", "JsDocInfoParser", "ParserRunner", "TypeSafeDispatcher", "JsDocTokenStream"], "com.google.javascript.rhino": ["IR", "ScriptRuntime", "Node", "JSDocInfoBuilder", "JSTypeExpression", "InputId"], "com.google.javascript.rhino.jstype": ["ErrorFunctionType", "ValueType", "Property", "SimpleSlot", "PropertyMap", "ArrowType", "AllType", "NoType", "NoResolvedType", "VoidType", "NoObjectType", "FunctionParamBuilder", "NullType", "UnionType", "NumberType", "ProxyObjectType", "InstanceObjectType", "FunctionBuilder", "JSType", "BooleanType", "PrototypeObjectType", "FunctionType", "NamedType", "UnknownType", "StringType", "UnionTypeBuilder", "JSTypeRegistry", "ObjectType"], "com.google.javascript.rhino.testing": ["BaseJSTypeTestCase"]}\n\nCovered test classes:\n{"com.google.javascript.jscomp": ["CompilerTypeTestCase", "TypeCheckTest"]}',
    },
]

completion = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=SEARCH_AGENT_TOOLS_OPENAI,
)

tool_call_msg = completion.choices[0].message.tool_calls[0]
tool_res_0 = {
    "role": "tool",
    "tool_call_id": tool_call_msg.id,
    "content": "No result, please try something else.",
}
messages.append(completion.choices[0].message)
messages.append(tool_res_0)

completion2 = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=SEARCH_AGENT_TOOLS_OPENAI,
)

print(completion2.choices[0].message.content)
