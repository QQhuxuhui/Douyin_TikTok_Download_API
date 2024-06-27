
import gui.douyin.config as  config # 导入 update_config 模块
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import json
import datetime
import csv
from PyQt5.QtWidgets import QFileDialog


from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫

DouyinWebCrawler = DouyinWebCrawler()


#更新cookie
def set_cookie(cookie):
    # 调用 update_config 模块中的 update_config_cookie 方法
    config.update_config_cookie(cookie)


    # 获取单个作品的ID
async def get_aweme_id(log_text, url):
        print(f'开始获取作品ID:{url}')
        data = await DouyinWebCrawler.get_aweme_id(url)
        return data

        

# 获取单个作品的信息
async def fetch_one_video(log_text, url):
        aweme_id = await get_aweme_id(log_text, url);
        if(aweme_id):
            data = await DouyinWebCrawler.fetch_one_video(aweme_id)
            return data;
        else:
            log_text.append_log("获取作品ID失败")
            return None
    
    
# 获取单个作品的评论，参数为作品链接
async def fetch_video_comments(log_text, url):
        print(f'获取作品信息：{url}')
        aweme_id = await get_aweme_id(log_text, url);
        print(f'获取作品ID：{aweme_id}')
        if(aweme_id):
            video_data = await fetch_one_video(log_text, url);
            statistics = video_data['aweme_detail']['statistics'] # 统计信息，点赞评论转发数量等
            digg_count = statistics['digg_count'] # 点赞
            share_count = statistics['share_count'] # 分享
            comment_count = statistics['comment_count'] # 评论
            collect_count = statistics['collect_count'] # 收藏
            all_comments = []
            current_page = 0
            page_size = 20
            # 总页数
            total_pages = (comment_count + page_size - 1) // page_size  # 向上取整计算总页数
            # print(f"要查询的总页数: {total_pages}")
            log_text.append_log(f"要查询的总页数: {total_pages}")
            while current_page <= total_pages:
                log_text.append_log(f"要查询的总页数: {total_pages}, 当前第{current_page}页")
                data = await DouyinWebCrawler.fetch_video_comments(aweme_id, current_page, 20)
                data = json.dumps(data, ensure_ascii=False, indent=2)
                all_comments.extend(data)
                current_page += 1
                yield data
        else:
            log_text.append_log("获取作品ID失败")
        

def update_comments_table(table, data):
    new_rows = 0
    json_data = json.loads(data)
    if 'comments' in json_data and isinstance(json_data['comments'], list):
        for comment in json_data['comments']:
            cid = comment['cid']
            text = comment['text']
            reply_comment_total = comment['reply_comment_total']
            create_time = comment['create_time']
            digg_count = comment['digg_count']
            status = comment['status']
            ip_label = comment['ip_label']
            nickName = comment['user']['nickname']
            uid = comment['user']['uid']
            dt_object = datetime.datetime.fromtimestamp(create_time)
            formatted_date = dt_object.strftime('%Y-%m-%d')
            
            formatted_comment = [
                formatted_date,
                cid,
                uid,
                nickName,
                ip_label,
                text,
                digg_count,
                reply_comment_total
            ]
            
            # Check if the comment already exists in the table
            exists = False
            num_rows = table.rowCount()
            for row in range(num_rows):
                if table.item(row, 1).text() == str(cid):  # Assuming cid is in the second column
                    exists = True
                    break
            
            if not exists:
                # Add the new comment to the table
                table.insertRow(num_rows)
                for col, value in enumerate(formatted_comment):
                    item = QTableWidgetItem(str(value))
                    table.setItem(num_rows, col, item)
                
                new_rows += 1
    
    print(f"Added {new_rows} new comments to the table.")
                
                
def export_table_to_csv(self,log_text, table_widget):
    path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
    if path:
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                # Write headers
                headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
                writer.writerow(headers)
                # Write data
                for row in range(table_widget.rowCount()):
                    row_data = []
                    for column in range(table_widget.columnCount()):
                        item = table_widget.item(row, column)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            QMessageBox.information(self, "成功", "表格数据已成功导出为CSV文件.")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出CSV文件时发生错误: {str(e)}")                