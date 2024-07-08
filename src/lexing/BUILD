python_library (
    name = "lexing",
    srcs = ["logic/lexing.py"],
    visibility= ["//src/..."],
)

python_test(
    name = "test_lexer",
    srcs = ["test/lexing_test.py"],
    deps = [
        ":lexing",
    ],
)