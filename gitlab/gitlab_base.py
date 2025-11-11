import os
from subprocess import run, CalledProcessError
import requests


def clone_pro(root_path, pro, branch=None):
    """
    Clones a git repository into a directory structure derived from its URL.
    Handles paths with spaces and raises an exception on failure.
    """
    # This logic for creating a local path is based on the original implementation.
    # It can be brittle, especially with different git URL formats.
    # e.g., 'git@gitlab.com:group/project.git' -> '/gitlab.com/group/project'
    local_path_str = pro.replace('git@', '/').replace(':', '/').replace('.git', '')

    # os.path.join treats paths starting with '/' as absolute on Unix,
    # or relative to the drive root on Windows. We strip it to ensure
    # the path is always relative to root_path.
    if local_path_str.startswith('/'):
        local_path_str = local_path_str[1:]

    destination_path = os.path.join(root_path, local_path_str)

    cmd = ['git', 'clone']
    if branch:
        cmd.extend(['-b', branch])

    cmd.append(pro)
    cmd.append(destination_path)
    print('now run ', cmd)

    try:
        # Execute the command. `check=True` raises CalledProcessError on non-zero exit codes.
        # Arguments are passed as a list to handle spaces correctly and prevent shell injection.
        run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        raise Exception("Command 'git' not found. Please make sure Git is installed and in your system's PATH.")
    except CalledProcessError as e:
        raise Exception(
            f"Failed to clone repository '{pro}'.\nGit command: {' '.join(cmd)}\nError: {e.stderr.strip()}") from e


def clone_pros(root_path, pros):
    for key, value in pros.items():
        clone_pro(root_path, key, value)


def group_pros(git_host, git_token, group_id, filters=None):
    projects = []

    # 获取当前 group 的所有项目
    response = requests.get(f'{git_host}/api/v4/groups/{group_id}/projects', headers={'PRIVATE-TOKEN': git_token})
    response.raise_for_status()
    projects.extend(response.json())

    # 获取当前 group 的所有子 group
    response = requests.get(f'{git_host}/api/v4/groups/{group_id}/subgroups', headers={'PRIVATE-TOKEN': git_token})
    response.raise_for_status()
    subgroups = response.json()
    if filters != None and filters.get('ignore_subgroups') != None:
        for filter in filters.get('ignore_subgroups'):
            for subgroup in subgroups:
                if subgroup['full_path'] == filter:
                    subgroups.remove(subgroup)

    # 递归获取每个子 group 的所有项目
    for subgroup in subgroups:
        projects.extend(group_pros(git_host, git_token, subgroup['id'], filters))

    if filters != None and filters.get('path_with_namespace') != None:
        for filter in filters.get('path_with_namespace'):
            for pro in projects:
                if pro['path_with_namespace'] == filter:
                    projects.remove(pro)

    return projects


def group_id(git_host, git_token, group_path):
    path_elems = group_path.split('/')

    group_rep = requests.get(f'{git_host}/api/v4/groups?search={path_elems[0]}', headers={'PRIVATE-TOKEN': git_token})
    group_rep.raise_for_status()

    if len(group_rep.json()) == 0:
        raise Exception(f'Group "{path_elems[0]}" not found.')

    for idx in range(1, len(path_elems)):
        id = group_rep.json()[0]['id']
        search = path_elems[idx]
        group_rep = requests.get(f'{git_host}/api/v4/groups/{id}/subgroups?search={search}',
                                 headers={'PRIVATE-TOKEN': git_token})
        group_rep.raise_for_status()
        if len(group_rep.json()) == 0:
            raise Exception(f'Group "{path_elems[0]}" not found.')

    return group_rep.json()[0]['id']
