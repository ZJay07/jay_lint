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
    srcs = ["test/test_naming_conventions.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "line_length",
    srcs = ["test/test_line_length.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "fix_unused_args",
    srcs = ["test/test_fix_unused_args.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "reorder_imports",
    srcs = ["test/test_reorder_imports.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "unused_reorder_imports",
    srcs = ["test/test_unused_reorder_imports.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "class",
    srcs = ["test/test_class.py"],
    deps = [
        ":lexing",
    ],
)

python_test(
    name = "force_fail",
    srcs = ["test/test_force_fail.py"],
    deps = [
        ":lexing",
    ],
)
# test