python_library (
    name = "lexing",
    srcs = ["logic/lexing.py"],
    visibility= ["//src/..."],
    deps = ["//third_party/python:pytest" , "//third_party/python:pluggy", "//third_party/python:iniconfig"],
)

python_test(
    name = "test_comment",
    srcs = ["test/test_comments.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "test_imports",
    srcs = ["test/test_imports.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "test_trailing_white_spaces",
    srcs = ["test/test_trailing_white_spaces.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "test_variables",
    srcs = ["test/test_variables.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "naming_convention",
    srcs = ["test/naming_conventions.py"],
    deps = [
        ":lexing",
    ],
)