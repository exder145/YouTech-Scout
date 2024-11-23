import os
import csv
import time
import random
from typing import List, Dict
from datetime import datetime, timedelta
import yt_dlp
import jieba
from collections import Counter
import requests
from urllib.parse import urlparse
import hashlib

# 在文件开头添加cookies文件路径配置
COOKIES_FILE = 'cookies.txt'  # 将cookies.txt文件放在与脚本相同目录下

class YouTubeCrawler:
    def __init__(self):
        """
        初始化YouTube爬虫
        """
        # 创建带时间戳的输出目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f'youtube_crawl_results_{timestamp}'
        self.thumbnails_dir = os.path.join(self.output_dir, 'thumbnails')
        
        # 创建输出目录和缩略图目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        
        self.search_categories = [
            {"zh": "AI创新", "en": "AI Innovation"},
            {"zh": "科技峰会", "en": "Tech Summit"}
        ]

    def download_thumbnail(self, url: str, video_title: str) -> str:
        """
        下载缩略图并返回保存路径，使用视频标题作为文件名
        """
        try:
            
            url = url.replace('vi_webp', 'vi')
            
            # 清理标题，移除不合法的文件名字符
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:100]  # 限制文件名长度
            
            # 生成文件名
            file_ext = '.jpg'  # 使用固定的jpg扩展名
            filename = f"{safe_title}{file_ext}"
            save_path = os.path.join(self.thumbnails_dir, filename)
            
            # 如果文件已存在，添加数字后缀
            base_path = save_path
            counter = 1
            while os.path.exists(save_path):
                name, ext = os.path.splitext(base_path)
                save_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 如果第一次请求失败，尝试其他格式
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except:
                # 尝试不同的缩略图格式
                video_id = url.split('/')[-2]
                fallback_formats = [
                    f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                ]
                
                for fallback_url in fallback_formats:
                    try:
                        response = requests.get(fallback_url, timeout=10)
                        response.raise_for_status()
                        break
                    except:
                        continue
                else:
                    raise Exception("所有缩略图格式都无法访问")
            
            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return save_path
            
        except Exception as e:
            print(f"下载缩略图失败 {url}: {e}")
            return ''

    def get_video_info(self, search_term: str) -> List[Dict]:
        """
        使用yt-dlp搜索并获取视频信息
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,  # 改为False以获取完整信息
            'no_check_certificates': True,
            'ignoreerrors': True,
            # 减少延迟时间
            'sleep_interval': 1,
            'max_sleep_interval': 2,
        }
        
        # 修改搜索数量从 ytsearch5 改为 ytsearch2
        search_url = f"ytsearch2:{search_term}"  # 每个关键词只搜索2个视频
        
        # 检查cookies文件
        cookies_path = os.path.join(os.path.dirname(__file__), COOKIES_FILE)
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
        else:
            print("警告：未找到cookies文件，这可能会影响搜索结果")
        
        videos = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    results = ydl.extract_info(search_url, download=False)
                    
                    if not results or 'entries' not in results:
                        print(f"未找到搜索结果: {search_term}")
                        return videos
                        
                    # 获取当前时间
                    current_date = datetime.now()
                    
                    for entry in results['entries']:
                        try:
                            time.sleep(random.uniform(0.5, 1.5))
                            
                            # 获取视频ID和标题
                            video_id = entry.get('id', '')
                            video_title = entry.get('title', '')
                            if not video_id or not video_title:
                                continue
                            
                            # 检查发布日期
                            upload_date = entry.get('upload_date', '')
                            if upload_date:
                                try:
                                    # 将YYYYMMDD格式转换为datetime对象
                                    video_date = datetime.strptime(upload_date, '%Y%m%d')
                                    # 计算视频发布至今的天数
                                    days_difference = (current_date - video_date).days
                                    
                                    # 如果视频超过730天（2年），跳过这个视频
                                    if days_difference > 730:
                                        print(f"跳过较旧的视频: {video_title}")
                                        continue
                                    
                                    # 格式化日期为YYYY-MM-DD
                                    formatted_date = video_date.strftime('%Y-%m-%d')
                                except:
                                    print(f"日期格式错误: {upload_date}")
                                    continue
                            else:
                                print(f"无法获取视频发布日期: {video_title}")
                                continue
                            
                            # 获取缩略图链接
                            thumbnail_url = ''
                            thumbnails = entry.get('thumbnails', [])
                            if thumbnails:
                                thumbnail_url = thumbnails[-1].get('url', '')
                            
                            if not thumbnail_url:
                                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                            
                            # 下载缩略图
                            thumbnail_path = self.download_thumbnail(thumbnail_url, video_title)
                            
                            video_data = {
                                'title': video_title,
                                'description': entry.get('description', '') or '',
                                'published_at': formatted_date,  # 使用格式化后的日期
                                'video_id': video_id,
                                'channel_title': entry.get('uploader', '') or '',
                                'thumbnail_path': thumbnail_path,
                                'video_link': f"https://www.youtube.com/watch?v={video_id}",
                                'duration': entry.get('duration', 0) or 0,
                                'view_count': entry.get('view_count', 0) or 0,
                                'like_count': entry.get('like_count', 0) or 0
                            }
                            
                            # 只检查必要的条件（时长和时间限制）
                            if 10 <= video_data['duration'] <= 240:
                                videos.append(video_data)
                            
                        except Exception as e:
                            print(f"处理视频信息时出错: {e}")
                            continue
                            
                except Exception as e:
                    print(f"搜索失败: {e}")
                    
        except Exception as e:
            print(f"搜索视频时出错: {e}")
        
        return videos

    def calculate_score(self, video_info: Dict) -> Dict:
        """
        根据五个维度的关键词计算评分
        """
        try:
            # 基础文本
            title = video_info.get('title', '') or ''
            description = video_info.get('description', '') or ''
            text = (title + ' ' + description).lower()
            
            # 定义五个维度的关键词及其权重
            dimensions = {
                'AI技术': {
                    'keywords': ['ai', '人工智能', '机器学习', '深度学习', '神经网络'],
                    'weight': 0.25
                },
                '云计算': {
                    'keywords': ['云计算', '云服务', '云平台', 'cloud', 'saas'],
                    'weight': 0.2
                },
                '数字化': {
                    'keywords': ['数字化', '数字转型', '智能化', '自动化', '信息化'],
                    'weight': 0.2
                },
                '创新': {
                    'keywords': ['创新', '革新', '突破', '前沿', '领先'],
                    'weight': 0.15
                },
                '解决方案': {
                    'keywords': ['解决方案', '应用', '落地', '实践', '案例'],
                    'weight': 0.2
                }
            }
            
            # 计算每个维度的得分
            dimension_scores = {}
            for dim_name, dim_data in dimensions.items():
                # 计算该维度下匹配的关键词数量
                matches = sum(1 for keyword in dim_data['keywords'] if keyword in text)
                # 计算维度得分（匹配数/关键词总数 * 权重）
                dim_score = (matches / len(dim_data['keywords'])) * dim_data['weight']
                dimension_scores[dim_name] = round(dim_score, 3)
            
            # 计算总分（所有维度得分之和）
            total_score = sum(dimension_scores.values())
            
            # 归一化总分（确保不超过1）
            total_score = min(total_score, 1)
            
            return {
                'total_score': round(total_score, 3),
                'dimension_scores': dimension_scores
            }
                
        except Exception as e:
            print(f"计算评分时出错: {e}")
            return {
                'total_score': 0,
                'dimension_scores': {
                    'AI技术': 0,
                    '云计算': 0,
                    '数字化': 0,
                    '创新': 0,
                    '解决方案': 0
                }
            }

    def search_videos(self, keywords: List[str]) -> List[Dict]:
        """
        搜索视频
        """
        all_videos = []
        
        for category in self.search_categories:
            for keyword in keywords:
                for lang, category_term in [('zh', category['zh']), ('en', category['en'])]:
                    print(f"正在搜索: 类别 '{category_term}' - 关键词 '{keyword}' - 语言: {lang}")
                    
                    search_term = f"{category_term} {keyword}"
                    videos = self.get_video_info(search_term)
                    
                    # 添加搜索相关信息
                    for video in videos:
                        video['category'] = f"{category['zh']} / {category['en']}"
                        video['search_keyword'] = keyword
                        video['search_language'] = lang
                        
                        # 直接计算评分
                        scores = self.calculate_score(video)
                        video.update(scores)
                    
                    all_videos.extend(videos)
                    
                    # 减少延迟时间
                    time.sleep(1)
        
        return all_videos

    def save_to_csv(self, results: List[Dict]):
        """
        将搜索结果保存为CSV文件
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(self.output_dir, f'youtube_search_results_{timestamp}.csv')
        
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = [
                    '标题', 
                    '描述', 
                    '发布时间', 
                    '视频ID', 
                    '频道名称', 
                    '缩略图文件名',
                    '分类', 
                    '搜索关键词', 
                    '视频链接',
                    '视频时长(秒)',
                    '搜索语言',
                    '总评分',
                    'AI技术得分',
                    '云计算得分',
                    '数字化得分',
                    '创新得分',
                    '解决方案得分'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    if not result:
                        continue
                    
                    try:
                        # 获取维度得分
                        dimension_scores = result.get('dimension_scores', {})
                        
                        row = {
                            '标题': result['title'],
                            '描述': result['description'],
                            '发布时间': result['published_at'],
                            '视频ID': result['video_id'],
                            '频道名称': result['channel_title'],
                            '缩略图文件名': os.path.basename(result['thumbnail_path']) if result['thumbnail_path'] else '',
                            '分类': result['category'],
                            '搜索关键词': result['search_keyword'],
                            '视频链接': result['video_link'],
                            '视频时长(秒)': result['duration'],
                            '搜索语言': result['search_language'],
                            '总评分': result.get('total_score', 0),
                            'AI技术得分': dimension_scores.get('AI技术', 0),
                            '云计算得分': dimension_scores.get('云计算', 0),
                            '数字化得分': dimension_scores.get('数字化', 0),
                            '创新得分': dimension_scores.get('创新', 0),
                            '解决方案得分': dimension_scores.get('解决方案', 0)
                        }
                        writer.writerow(row)
                    except Exception as e:
                        print(f"保存单条结果时出错: {e}")
                        continue
                    
            print(f"结果已成功保存到 {csv_file}")
            
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")

    def crawl_and_save(self, keywords: List[str]):
        """
        爬取视频并保存结果
        """
        videos = self.search_videos(keywords)
        self.save_to_csv(videos)
        print(f"已完成爬取，共找到 {len(videos)} 个视频")

class SearchTermProcessor:
    def __init__(self):
        self.stop_words = set(['的', '了', '和', '与', '或', '在', '是'])
    
    def process_query(self, query: str) -> tuple:
        # 分词
        words = jieba.cut_for_search(query)
        # 清理和标准化
        words = [w.lower().strip() for w in words]
        # 过滤停用词
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        # 统计词频
        term_freq = Counter(words)
        
        return list(term_freq.keys()), term_freq

def main():
    crawler = YouTubeCrawler()
    
    # 减少测试关键词
    keywords = [
        "AI创新",
        "科技峰会"
    ]
    
    try:
        crawler.crawl_and_save(keywords)
    except Exception as e:
        print(f"爬取过程中断: {e}")

if __name__ == '__main__':
    main()