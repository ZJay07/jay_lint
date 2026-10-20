python_binary(
    name = "main",
    main = "main.py",
    deps = ["//src/lexing"],
)

python_library (
    name = "cli",
    srcs = ["cli.py", "config.py"],
    visibility= ["//Jay_lint/...", "//src/..."],
    deps = ["//src/lexing", "//src/lexing:ts_linter"],
)