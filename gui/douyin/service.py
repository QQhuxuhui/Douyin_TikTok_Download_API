
import gui.douyin.config as  config # 导入 update_config 模块
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
import json
import datetime
import time
import asyncio
import csv
import os
from PyQt5.QtWidgets import QFileDialog
import aiofiles
import httpx
import zipfile
from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫
from app.web.views.ViewsUtils import ViewsUtils
DouyinWebCrawler = DouyinWebCrawler()
from crawlers.hybrid.hybrid_crawler import HybridCrawler
HybridCrawler = HybridCrawler()

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


async def download_file_batch(log_text, input_data):
    url_lists = ViewsUtils.find_url(input_data)
    # 解析开始时间
    start = time.time()
    # 成功/失败统计
    success_count = 0
    failed_count = 0
    # 链接总数
    url_count = len(url_lists)
    # 解析成功的url
    success_list = []
    # 解析失败的url
    failed_list = []
    # 遍历链接列表
    for url in url_lists:
        # 链接编号
        url_index = url_lists.index(url) + 1
        # 解析
        try:
            download_file_one(url)
        except Exception as e:
            error_msg = str(e)
            log_text.append_log(f"视频下载失败: {url}, 当前第{url_index}个，失败原因：{error_msg}")
            failed_count += 1
            failed_list.append(url)
            continue
        
        
async def fetch_data(url: str, headers: dict = None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } if headers is None else headers.get('headers')
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # 确保响应是成功的
        return response
        
async def download_file_one(log_text, url):

    # 开始解析数据/Start parsing data
    try:
        data = await HybridCrawler.hybrid_parsing_single_video(url, minimal=True)
    except Exception as e:
        code = 400
        log_text.append_log(f"视频下载失败: {url}，失败原因：{str(e)}")
        return;

    # 开始下载文件/Start downloading files
    try:
        data_type = data.get('type')
        platform = data.get('platform')
        aweme_id = data.get('aweme_id')
        file_prefix = config.get("API").get("Download_File_Prefix")
        download_path = os.path.join(config.get("API").get("Download_Path"), f"{platform}_{data_type}")

        # 确保目录存在/Ensure the directory exists
        os.makedirs(download_path, exist_ok=True)

        # 下载视频文件/Download video file
        if data_type == 'video':
            file_name = f"{file_prefix}{platform}_{aweme_id}.mp4"
            url = data.get('video_data').get('nwm_video_url_HQ') 
            file_path = os.path.join(download_path, file_name)


            # 获取视频文件
            response = await fetch_data(url) if platform == 'douyin' else await fetch_data(url, headers=await HybridCrawler.TikTokWebCrawler.get_tiktok_headers())

            # 保存文件
            async with aiofiles.open(file_path, 'wb') as out_file:
                await out_file.write(response.content)

            # 返回文件内容
            # return FileResponse(path=file_path, filename=file_name, media_type="video/mp4")

        # 下载图片文件/Download image file
        elif data_type == 'image':
            # 压缩文件属性/Compress file properties
            zip_file_name = f"{file_prefix}{platform}_{aweme_id}_images.zip"
            zip_file_path = os.path.join(download_path, zip_file_name)

            # 获取图片文件/Get image file
            urls = data.get('image_data').get('no_watermark_image_list')
            image_file_list = []
            for url in urls:
                # 请求图片文件/Request image file
                response = await fetch_data(url)
                index = int(urls.index(url))
                content_type = response.headers.get('content-type')
                file_format = content_type.split('/')[1]
                file_name = f"{file_prefix}{platform}_{aweme_id}_{index + 1}.{file_format}"
                file_path = os.path.join(download_path, file_name)
                image_file_list.append(file_path)

                # 保存文件/Save file
                async with aiofiles.open(file_path, 'wb') as out_file:
                    await out_file.write(response.content)

            # 压缩文件/Compress file
            with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                for image_file in image_file_list:
                    zip_file.write(image_file, os.path.basename(image_file))

            # # 返回压缩文件/Return compressed file
            # return FileResponse(path=zip_file_path, filename=zip_file_name, media_type="application/zip")

    # 异常处理/Exception handling
    except Exception as e:
        print(e)
        log_text.append_log(f"视频下载失败: {url}，失败原因：{str(e)}")
        
                
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