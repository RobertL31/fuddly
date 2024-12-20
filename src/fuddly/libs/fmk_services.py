import os
from importlib.util import find_spec
from importlib.metadata import entry_points

import fuddly.framework.global_resources as gr
from fuddly.framework.plumbing import _populate_projects as populate_projects

def get_each_project_module() -> []:

    project_modules = []

    # Project from user (FS)
    projects = populate_projects(gr.user_projects_folder, prefix="user_projects", projects=None)
    for dname, file_list in projects.items():
        prefix = dname.replace(os.sep, ".") + "."
        for name in file_list:
            m = find_spec(prefix+name)
            # This should never happen
            if m is None or m.origin is None:
                print(f"{prefix+name} detected as a module in {gr.fuddly_data_folder}/user_projects,"
                      " but could not be imported")
                continue
            project_modules.append(m)

    # Projects from modules
    for ep in entry_points(group=gr.ep_group_names["projects"]):
        m = find_spec(ep.module)
        # If an entry point does not actually point to a module
        # i.e. somebody broke their package
        if m is None or m.origin is None:
            # the entry point is not a module, let's just ignore it
            print(f"*** {ep.module} is not a python module, check your installed modules ***")
            continue
        project_modules.append(m)

    return project_modules