from subprocess import run
import requests

def clone_pro(root_path, pro, branch = None):
    local_path = pro.replace('git@', '/').replace(':','/').replace('.git', '')
    cmd = 'git clone ' + pro
    if branch != None:
        cmd += ' -b ' + branch
    run(cmd + ' ' + root_path + local_path, shell = True)

def clone_pros(root_path, pros):
    for key, value in pros.items():
        clone_pro(root_path, key, value)

def group_pros(git_host, git_token, group_id):
    projects = []

    # 获取当前 group 的所有项目
    response = requests.get(f'{git_host}/api/v4/groups/{group_id}/projects', headers={'PRIVATE-TOKEN': git_token})
    response.raise_for_status()
    projects.extend(response.json())

    # 获取当前 group 的所有子 group
    response = requests.get(f'{git_host}/api/v4/groups/{group_id}/subgroups', headers={'PRIVATE-TOKEN': git_token})
    response.raise_for_status()
    subgroups = response.json()

    # 递归获取每个子 group 的所有项目
    for subgroup in subgroups:
        projects.extend(group_pros(git_host, git_token, subgroup['id']))

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