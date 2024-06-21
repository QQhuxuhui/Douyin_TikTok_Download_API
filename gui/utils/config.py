import os

def get_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    config_path = os.path.join(project_root, 'config.yaml')
    return config_path