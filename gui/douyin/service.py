import requests
import douyin.config as  config # 导入 update_config 模块
from PyQt5.QtWidgets import QTableWidgetItem
import json
import datetime

web_ip = config.get_web_ip()
web_port = config.get_web_port()

base_url = f"http://{web_ip}:{web_port}" + "/api/douyin/web"
print(base_url)

#更新cookie
def set_cookie(cookie):
    # 调用 update_config 模块中的 update_config_cookie 方法
    config.update_config_cookie(cookie)


# 获取单个作品的ID
def get_aweme_id(url):
    params = {
        "url": url
    }
    # 发送GET请求
    url = base_url + "/get_aweme_id";
    print(url)
    response = requests.get(url, params=params)
    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()
        print("获取作品ID成功:")
        print(data)
        return data.get('data');
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.text)
        return None
        

# 获取单个作品的信息
def fetch_one_video(url):
    aweme_id = get_aweme_id(url);
    if(aweme_id):
        # Query parameters
        params = {
            "aweme_id": aweme_id  # 替换为实际的视频ID
        }
        # 发送GET请求
        url = base_url + "/fetch_one_video";
        response = requests.get(url, params=params)
        # 检查响应状态码
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            return data
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)
            return None
    else:
        print("获取作品ID失败")
        return None
    
    
# 获取单个作品的评论，参数为作品链接
def fetch_video_comments(url):
    aweme_id = get_aweme_id(url);
    if(aweme_id):
        video_data = fetch_one_video(url);
        statistics = video_data['data']['aweme_detail']['statistics'] # 统计信息，点赞评论转发数量等
        digg_count = statistics['digg_count'] # 点赞
        share_count = statistics['share_count'] # 分享
        comment_count = statistics['comment_count'] # 评论
        collect_count = statistics['collect_count'] # 收藏
        all_comments = []
        current_page = 0
        page_size = 20
        # 总页数
        total_pages = (comment_count + page_size - 1) // page_size  # 向上取整计算总页数
        print(f"要查询的总页数: {total_pages}")
        while current_page <= total_pages:
            print(f"要查询的总页数: {total_pages}, 当前第{current_page}页")
            # Query parameters
            params = {
                "aweme_id": aweme_id,  # 替换为实际的视频ID
                "cursor": current_page,
                "count": 20
            }
            # 发送GET请求
            url = base_url + "/fetch_video_comments";
            response = requests.get(url, params=params)
            # 检查响应状态码
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                # print("获取评论数据成功:")
                # print(data)
                all_comments.append(data)
                # return data
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(response.text)
                return None
            current_page += 1
        return all_comments;
    else:
        print("获取作品ID失败")
        return None
    

# 更新GUI上的评论表格
def update_comments_table(table, comments_data):
        # 格式化data
        comments_table_data=[];
        for data in comments_data:
            json_data = json.loads(json.dumps(data, ensure_ascii=False, indent=2))
            # 检查是否存在comments字段，并且是一个列表
            if 'data' in json_data and 'comments' in json_data['data'] and isinstance(json_data['data']['comments'], list):
                # 遍历comments列表
                for comment in json_data['data']['comments']:
                    cid = comment['cid']
                    text = comment['text']
                    reply_comment_total = comment['reply_comment_total'] # 评论回复数量
                    create_time = comment['create_time']
                    digg_count = comment['digg_count'] # 评论点赞数量
                    status = comment['status']
                    ip_label = comment['ip_label']
                    nickName = comment['user']['nickname']
                    uid = comment['user']['uid']
                    dt_object = datetime.datetime.fromtimestamp(create_time)
                    # 格式化日期字符串
                    formatted_date = dt_object.strftime('%Y-%m-%d')
                    # 在这里可以对每条评论进行处理，例如输出或者存储到表格中
                    # 组装成指定格式的列表
                    formatted_comment = [
                        formatted_date,  # 如果需要日期格式化，可以使用datetime库进行转换
                        cid,
                        uid,
                        nickName,  # 你的文章标题
                        ip_label,
                        text,  # 你的文章内容
                        digg_count,
                        reply_comment_total
                    ]
                    comments_table_data.append(formatted_comment)
            else:
                print("JSON数据格式不正确或缺少必要字段")
        # data 是一个二维列表，包含需要更新的数据
        num_rows = len(comments_table_data)
        num_cols = len(comments_table_data[0]) if num_rows > 0 else 0

        table.setRowCount(num_rows)
        table.setColumnCount(num_cols)

        for row in range(num_rows):
            for col in range(num_cols):
                item = QTableWidgetItem(str(comments_table_data[row][col]))
                table.setItem(row, col, item)