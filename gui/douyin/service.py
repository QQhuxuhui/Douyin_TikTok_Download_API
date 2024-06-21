import os
# YAML
import yaml
from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫

DouyinWebCrawler = DouyinWebCrawler()

# Load Config

# 读取上级再上级目录的配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../config.yaml')


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.abspath(os.path.join(script_dir, '../../'))
    
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


Host_IP = config['API']['Host_IP']
Host_Port = config['API']['Host_Port']



    



