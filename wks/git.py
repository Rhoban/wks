import subprocess
import os
from . import env, message, env
import threading


def parse_repository_name(name):
    parts = name.split("/")

    if len(parts) != 2:
        message.die("Bad repository name: " + name)

    repository = {"vendor": parts[0], "name": parts[1], "branch": None, "tag": None}

    markers = {"#": "branch", "@": "tag"}

    for marker in markers:
        if marker in repository["name"]:
            name, value = repository["name"].split(marker, 1)
            repository["name"] = name
            repository[markers[marker]] = value

    repository["directory"] = (
        env.sources_directory + "/" + repository["vendor"] + "/" + repository["name"]
    )
    repository["git"] = "git@github.com:%s/%s.git" % (
        repository["vendor"],
        repository["name"],
    )
    repository["full_name"] = "%s/%s" % (repository["vendor"], repository["name"])

    return repository


def install(repository_name, source):
    repository = parse_repository_name(repository_name)

    if not os.path.exists(repository["directory"]):
        message.bright("* Installing " + repository_name + "...")
        vendor_dir = os.path.dirname(repository["directory"])

        if not os.path.exists(vendor_dir):
            os.makedirs(vendor_dir)

        branchName = ""
        if repository["branch"]:
            branchName = "--branch " + repository["branch"]
        if repository["tag"]:
            branchName = "--branch " + repository["tag"]

        cmd = "git clone %s %s %s" % (
            branchName,
            repository["git"],
            repository["directory"],
        )

        message.run_or_fail(cmd)

        config = env.get_config(repository["directory"])
        if config and "install" in config:
            for command in config["install"]:
                cmd = "cd %s; %s" % (repository["directory"], command)
                message.run_or_fail(cmd)

        return True
    else:
        if repository["branch"]:
            current_branch = branch(repository["directory"])
            if current_branch != repository["branch"]:
                print(
                    message.warn(
                        "WARNING: %s wants branch %s for %s, but it is currently %s"
                        % (
                            source,
                            repository["branch"],
                            repository["full_name"],
                            current_branch,
                        )
                    )
                )
        elif repository["tag"]:
            current_tag = tag(repository["directory"])
            if current_tag != repository["tag"]:
                print(
                    message.warn(
                        "WARNING: %s wants tag %s for %s, but it is currently %s"
                        % (
                            source,
                            repository["tag"],
                            repository["full_name"],
                            current_tag,
                        )
                    )
                )

        return False


def get_directories(directory=None):
    directories = []
    if directory is None:
        directory = env.sources_directory

    if not os.path.isdir(directory):
        message.die("Directory %s does not exists" % directory)

    subdirectories = [entry.name for entry in os.scandir(directory)]
    subdirectories.sort()

    for entry in subdirectories:
        full_name = directory + "/" + entry

        if os.path.isdir(full_name):
            if os.path.isdir(full_name + "/.git"):
                directories.append(full_name)
            else:
                directories += get_directories(full_name)

    return directories


def scan_dependencies(directory):
    changed = False
    config = env.get_config(directory)

    if config and "deps" in config:
        for entry in config["deps"]:
            if install(entry, os.path.basename(directory)):
                changed = True

    return changed


def scan_all_dependencies():
    message.bright("* Scanning all dependencies")
    changed = True

    while changed:
        changed = False
        for directory in get_directories():
            if scan_dependencies(directory):
                changed = True


def global_command(command, vendor_filter=None):
    message.bright("* Running global command: %s" % command)

    use_threads = os.getenv("WKS_NO_THREADS") is None
    directories = get_directories()

    threads: list[threading.Thread] = [None] * len(directories)
    processes: list[subprocess.CompletedProcess] = threads.copy()
    has_error: bool = False

    def thread_func(index: int, dir: str, cmd: str):
        processes[index] = subprocess.run(
            cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dir
        )

    def show_output(process):
        if process.returncode != 0:
            print(message.error(process.stdout.decode()))
        else:
            print(process.stdout.decode())

    for index, directory in enumerate(directories):
        if vendor_filter is not None:
            parts = directory.split("/")
            vendor = parts[-2]
            if vendor.lower() != vendor_filter.lower():
                continue

        if use_threads:
            threads[index] = threading.Thread(
                None, thread_func, args=(index, directory, command)
            )
            threads[index].start()
        else:
            message.bright("> %s" % directory)
            thread_func(index, directory, command)
            show_output(processes[index])
            if processes[index].returncode != 0:
                has_error = True

    if use_threads:
        for index, directory in enumerate(directories):
            threads[index].join()
            message.bright("- In %s ..." % os.path.realpath(directory))
            show_output(processes[index])
            if processes[index].returncode != 0:
                has_error = True

    print("")
    if has_error:
        print(message.error("Some commands failed"))


def status(directory):
    output = subprocess.getoutput("cd %s; git status --porcelain=v1" % directory)
    return output


def branch(directory):
    output = subprocess.getoutput("cd %s; git rev-parse --abbrev-ref HEAD" % directory)
    return output


def tag(directory):
    output = subprocess.getoutput("cd %s; git describe" % directory)
    return output


def is_ahead(directory):
    ret, output = subprocess.getstatusoutput("cd %s; git rev-list @{u}.." % directory)
    return ret == 0 and output.strip() != ""
