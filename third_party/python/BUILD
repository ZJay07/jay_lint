package(default_visibility =["PUBLIC"])

pip_library(
    name = "pytest",
    version = "7.4.3",
)

pip_library(
    name = "pluggy",
    version = "1.3.0",
)

pip_library(
    name = "iniconfig",
    version = "2.0.0",
)

pip_library(
    name = "tree_sitter",
    package_name = "tree-sitter",
    version = "0.26.0",
)

pip_library(
    name = "tree_sitter_typescript",
    package_name = "tree-sitter-typescript",
    version = "0.23.2",
    deps = [":tree_sitter"],
)
