python_library (
    name = "lexing",
    srcs = ["logic/lexing.py"],
    visibility= ["//src/..."],
    deps = ["//third_party/python:pytest" , "//third_party/python:pluggy", "//third_party/python:iniconfig"],
)

python_test(
    name = "test_lexer",
    srcs = ["test/lexing_test.py"],
    deps = [
        ":lexing",
    ],
)