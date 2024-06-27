import os
import socket
from ruamel.yaml import YAML
import yaml

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('127.0.0.1', port)) != 0

def update_config_port(new_port, config_path):
    yaml = YAML()
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file)
    
    config['API']['Host_Port'] = new_port

    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file)

def find_available_port(start_port=80, end_port=65535):
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    return None

def get_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    config_path = os.path.join(project_root, 'config.yaml')
    return config_path



def main():
    print("开始检测可用端口")
    config_path = get_config_path()
    available_port = find_available_port()
    print("检测到可用端口：", available_port)
    if available_port is None:
        raise Exception("No available port found between 80 and 65535")

    # print(f"Found available port: {available_port}")
    update_config_port(available_port, config_path)
    # print(f"Updated {config_path} with port {available_port}")
 
# 获取抖音配置文件
def get_douyun_config_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(script_dir, '../../crawlers/douyin/web'))
    config_path = os.path.join(config_path, 'config.yaml')
    return config_path

# 更新抖音cookie
def update_config_cookie(cookie):  
    config_path = get_douyun_config_path()
    yaml = YAML()
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.load(file)
    
    config['TokenManager']['douyin']['headers']['Cookie'] = cookie

    with open(config_path, 'w', encoding='utf-8') as file:
        yaml.dump(config, file)

# 获取web地址
def get_web_ip():
    with open(get_config_path(), 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config.get('API', {}).get('Host_IP', None)

# 获取web端口
def get_web_port():
    with open(get_config_path(), 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config.get('API', {}).get('Host_Port', None)

    
if __name__ == "__main__":
    main()
