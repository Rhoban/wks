import os
import stat
from . import env, git


def generate():
    for directory in git.get_directories():
        config = env.get_config(directory)
        if config is None:
            continue

        if "scripts" in config:
            for name in config["scripts"]:
                entry = config["scripts"][name]

                cd = None
                if type(entry) is str:
                    command = entry
                elif type(entry) is dict:
                    command = entry["run"]
                    cd = entry.get("cd", None)

                bash_script = "#!/bin/bash\n"
                bash_script += "\n"
                if cd is not None:
                    bash_script += f"cd {directory}/{cd}\n"
                bash_script += f"{directory}/{command} $*"

                script_filename = f"scripts/{name}"

                os.makedirs("scripts", exist_ok=True)
                with open(script_filename, "w") as f:
                    f.write(bash_script)
                st = os.stat(script_filename)
                os.chmod(script_filename, st.st_mode | stat.S_IEXEC)
