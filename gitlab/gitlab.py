from gitlab.gitlab_base import group_id, group_pros, clone_pros

def clone_group_pros(root_path, git_host, git_token, group_path, branch=None, filters = None):
    # 根据 group 获取所有项目
    pros = {}
    for pro in group_pros(git_host, git_token, group_id(git_host, git_token, group_path), filters):
        pros[pro['ssh_url_to_repo']] = branch
    clone_pros(root_path, pros)