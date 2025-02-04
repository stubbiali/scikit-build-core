# FAQs

This section covers common needs.

## Starting a new project

The easiest way to get started is to use the [Scientific Python cookie][], which
makes a new project following the [Scientific Python Development Guidelines][].
Scikit-build-core is one of the backends you can select. The project will have a
lot of tooling prepared for you as well, including pre-commit checks and a
noxfile; be sure to read the guidelines to see what is there and how it works.

Another option is the [pybind11 example][].

In the future, a CLI interface with a new project generator is planned.

## Multithreaded builds

For most generators, you can control the parallelization via a CMake define:

```bash
pip install -Ccmake.define.CMAKE_BUILD_PARALLEL_LEVEL=8 .
```

or an environment variable:

```bash
CMAKE_BUILD_PARALLEL_LEVEL=8 pip install .
```

The default generator on Unix-like platforms is Ninja, which automatically tries
to run in parallel with the number of cores on your machine.

## Dynamic setup.py options

While we will eventually have some dynamic options, most common needs can be
moved into your `CMakeLists.txt`. For example, if you had a custom `setup.py`
option (which setuptools has deprecated as well), you can make it a CMake option
and then pass it with `-Ccmake.define.<OPTION_NAME>=<value>`. If you need to
customize configuration options, try `[[tool.scikit-build.overrides]]`. If that
is missing some value you need, please open an issue and let us know.

## Finding Python

One common mistake when using FindPython is to forget to only request the
`Development.Module` component. If you request `Development`, you will also
require the `Development.Embed` component, which will require the Python
libraries to be found for linking. When building a module on Unix, you do not
link to Python - the Python symbols are already loaded in the interpreter.
What's more, the manylinux image (which is used to make redistributable Linux
wheels) does not have the Python libraries, both to avoid this mistake, and to
reduce size.

<!-- prettier-ignore-start -->

[scientific python cookie]: https://github.com/scientific-python/cookie
[scientific python development guide]: https://learn.scientific-python.org/development
[pybind11 example]: https://github.com/pybind/scikit_build_example

<!-- prettier-ignore-end -->
