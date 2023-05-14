# wks: Simple CMake workspace manager

## How it works

The basic purpose of `wks` is to spawn repositories to build a project, then generate a `CMakeLists.txt`
containing `add_subdirectory()` directives for all of them.

This way, the project can be built using the top-level generated `CMakeLists.txt`.

## Usage

The following commands are available:

* `wks install [repository]`: If a repository is given, `wks` will install it first. Then, `wks` will scan for
  dependencies in the `wks.yml` files (see below) and install them until all requirements are met. This way, it is
  possible that dependencies of dependencies are installed. Calling `wks install` without repository argument will
  cause dependencies scan. The `CMakeLists.txt` will eventually be generated.
* `wks cmake`: This will cause the `CMakeLists.txt` to be re-generated.
* `wks build [target]`: Will create a build and run it. `wks` will try to create a Ninja build, and
  fall back to makefiles if it is not available. The `[target]` you can pass will be given to the build command
  (`make [target]` or `ninja [target]`). The build will be stored in `build/` directory.
* `wks pull`: Will run a `git pull` in all repositories. This will then scan for dependencies (equivalent to `wks install`
  with no argument) and re-generate the `CMakeLists.txt`.
* `wks status`: Gives insight on the status of your repositories, this will check for:
  * Untracked files
  * Changes without commits
  * Changes commited but not pushed

All sources will be stored in `src/`, under `src/vendor/repository`.

## Repositories format

All repositories are fetched for GitHub, and repositories can have those formats:

* `vendor/repository`
* `vendor/repository#branch`
* `vendor/repository@tag`

## The `wks.yml` file

The `wks.yml` can contain the following sections:

* `deps`: a list of dependencies that the repository want to be installed
* `optional`: a list of optional dependencies, they will not be installed but it ensure that the projects will appear
  in the proper order in the generated `CMakeLists.txt`
* `cmakes`: if the `CMakeLists.txt` for this repository is not at the top level (or not unique), you can specify them
  using this section
* `install`: a list of shell command that should be run post install
* `cmake_prefix`: a list of directories to be added to `CMAKE_PREFIX_PATH`

An example is:

```yaml
deps:
    - rhoban/utils@v1.0
    - rhoban/geometry@v2.0

cmakes:
    - client
    - server
```