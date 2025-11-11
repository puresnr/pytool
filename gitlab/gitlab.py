from gitlab.gitlab_base import group_id, group_pros, clone_pros

def clone_group_pros(root_path, git_host, git_token, group_path, branch=None, filters = None):
    """
    Clones all projects from a specific GitLab group.

    This function retrieves all projects within a given GitLab group (and its subgroups)
    and clones them to a specified local directory.

    Args:
        root_path (str): The local root directory where the projects will be cloned.
        git_host (str): The URL of the GitLab instance (e.g., 'https://gitlab.com').
        git_token (str): Your personal GitLab access token.
        group_path (str): The full path of the group on GitLab (e.g., 'my-group/my-subgroup').
        branch (str, optional): The specific branch to clone for all projects. If None, the default branch is used. Defaults to None.
        filters (list, optional): A list of keywords to filter projects by name. Only projects whose names contain
                                  any of the keywords will be cloned. Defaults to None.
    """
    pros = {}
    for pro in group_pros(git_host, git_token, group_id(git_host, git_token, group_path), filters):
        pros[pro['ssh_url_to_repo']] = branch
    clone_pros(root_path, pros)
