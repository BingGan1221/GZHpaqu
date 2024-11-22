import requests
import time
import random
import pandas as pd
import math
import os
import json

class WeChatCrawler:
    def __init__(self):
        # 目标URL - 修改为正确的API接口
        self.url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
        
        # 请求头参数
        self.headers = {
            "Cookie": "appmsglist_action_3942452920=card; qq_domain_video_guid_verify=a44a500e4fa2f923; _qimei_uuid42=17c0c110220100c03ccc17452527479656273fbfbe; _qimei_fingerprint=d3c60c3b650720acc14bcdd8e80ce840; _qimei_q36=; _qimei_h38=2db880e33ccc1745252747960200000ec17c0c; pgv_pvid=6040991410; pac_uid=0_BDr7JKPpfwt6P; RK=wCFwmErnz7; ptcz=342484dc9acedc947214c55268638a3a996d6e77f52adfcc12b5579c3602df13; eas_sid=31R7G2n9c6K0T0z3L1i0F7h234; wxuin=32089343012574; ua_id=aKAkjKnquMIbiLe1AAAAAJLMIBMMWuOskpkdpTTly30=; mm_lang=zh_CN; rand_info=CAESIBSkzBwm/OeekM47PYk+ZRJ6I3GxDcLE9iowKg5BwQ0J; slave_bizuin=3942452920; data_bizuin=3942452920; bizuin=3942452920; data_ticket=R7vz0bUMtC4isBpcY4/ilKbY6NFaDgwbmUI5Y42LwSrpwz0MqL0tWtSAA0ThOgd9; slave_sid=XzZUaGdzWVhUdFJqajJGbmMzZFhwVTlESjJ1Nm54NlhNUkRDdWEwVDNrbTUwczBLQUdYY0FaN2lyVldZS0R5NnZ6ZWtCR1IyMXhnc3I0cWhESGY2eGR6WWtOZkZUZ3BVQWgwVm81NFhSWHpDWTVVbzdvWUh3eHU1eUYzcDNFYVRHdWh1U1UyelJqZXhXVkRW; slave_user=gh_3b25559548a1; xid=02a2b6ca03c7d1c0a053bbba3ea40671; ts_uid=9280525408; rewardsn=; wxtokenkey=777; _clck=3942452920|1|fr3|0; _clsk=9j1xkh|1732249091229|27|1|mp.weixin.qq.com/weheat-agent/payload/record",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=11845441&lang=zh_CN"
        }
        
        # 业务参数 - 更新为正确的参数
        self.data = {
            "sub": "list",
            "search_field": "null",
            "begin": "0",
            "count": "5",
            "query": "",
            "fakeid": "MjM5MjQ4MzMwMA==",
            "type": "101_1",
            "free_publish_type": "1",
            "sub_action": "list_ex",
            "token": "11845441",
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        
        # 添加公众号名称
        self.account_name = "VIVA旅行家"

    def get_total_articles(self):
        """获取文章总数和页数"""
        try:
            response = requests.get(self.url, headers=self.headers, params=self.data)
            response_json = response.json()
            
            # 解析 publish_page 字段
            if 'publish_page' in response_json:
                import json
                publish_data = json.loads(response_json['publish_page'])
                total_count = int(publish_data.get('total_count', 100))
                print(f"总文章数: {total_count}")
                total_pages = int(math.ceil(total_count / 5))
                return total_count, total_pages
            
            return 100, 20  # 默认值
        except Exception as e:
            print(f"获取文章总数时出错: {str(e)}")
            return 100, 20

    def crawl_articles(self, max_pages=20, target_count=100):
        """爬取文章信息"""
        all_content = []
        total_collected = 0
        
        try:
            for i in range(max_pages):
                if total_collected >= target_count:
                    break
                    
                self.data["begin"] = str(i * 5)
                
                response = requests.get(self.url, headers=self.headers, params=self.data)
                response_json = response.json()
                
                if 'publish_page' in response_json:
                    publish_data = json.loads(response_json['publish_page'])
                    publish_list = publish_data.get('publish_list', [])
                    
                    for item in publish_list:
                        if total_collected >= target_count:
                            break
                            
                        try:
                            publish_info = json.loads(item['publish_info'])
                            for detail in publish_info.get('appmsgex', []):
                                if total_collected >= target_count:
                                    break
                                    
                                # 获取时间戳
                                timestamp = publish_info.get('sent_info', {}).get('time')
                                if timestamp:
                                    try:
                                        # 转换时间戳为日期时间
                                        create_time = time.strftime("%Y-%m-%d %H:%M:%S", 
                                                                  time.localtime(int(timestamp)))
                                    except:
                                        create_time = "未知时间"
                                else:
                                    create_time = "未知时间"
                                    
                                article_info = [
                                    detail.get('title', ''),  # 标题
                                    detail.get('link', ''),   # 链接
                                    create_time               # 创建时间
                                ]
                                
                                if article_info[0]:  # 只添加有标题的文章
                                    all_content.append(article_info)
                                    total_collected += 1
                                    print(f"已添加文章 {total_collected}/{target_count}: {article_info[0]} ({create_time})")
                                    
                        except Exception as e:
                            print(f"处理单篇文章时出错: {str(e)}")
                            continue
                    
                    print(f"进度: {i+1}/{max_pages}页 | 已收集{total_collected}/{target_count}篇文章")
                    time.sleep(random.randint(1, 2))
            
            # 只在最后保存一次数据
            if all_content:
                self._save_data(all_content, mode='w')  # 使用覆盖模式而不是追加模式
                
        except Exception as e:
            print(f"爬取出错: {str(e)}")
            if all_content:
                self._save_data(all_content, is_error=True, mode='w')

    def _save_data(self, content_list, is_error=False, mode='w'):
        """保存数据的内部方法"""
        try:
            save_dir = os.path.dirname(os.path.abspath(__file__))
            filename = f"{self.account_name}_error.csv" if is_error else f"{self.account_name}.csv"
            save_path = os.path.join(save_dir, filename)
            
            df = pd.DataFrame(
                content_list,
                columns=['title', 'link', 'create_time']
            )
            
            # 始终使用传入的模式，默认为覆盖模式
            df.to_csv(save_path, mode=mode, encoding='utf-8-sig', 
                     index=False, header=True)
            print(f"已保存{len(content_list)}篇文章到 {filename}")
            
        except Exception as e:
            print(f"保存失败: {str(e)}")

    def search_articles(self, keyword, max_pages=20):
        """搜索包含关键词的文章"""
        search_results = []
        
        try:
            for i in range(max_pages):
                self.data["begin"] = str(i * 5)
                
                response = requests.get(self.url, headers=self.headers, params=self.data)
                response_json = response.json()
                
                if 'publish_page' in response_json:
                    publish_data = json.loads(response_json['publish_page'])
                    publish_list = publish_data.get('publish_list', [])
                    
                    for item in publish_list:
                        try:
                            publish_info = json.loads(item['publish_info'])
                            for detail in publish_info.get('appmsgex', []):
                                title = detail.get('title', '')
                                if keyword.lower() in title.lower():  # 不区分大小写搜索
                                    timestamp = publish_info.get('sent_info', {}).get('time')
                                    create_time = time.strftime("%Y-%m-%d %H:%M:%S", 
                                                              time.localtime(int(timestamp))) if timestamp else "未知时间"
                                    
                                    search_results.append({
                                        'title': title,
                                        'link': detail.get('link', ''),
                                        'create_time': create_time
                                    })
                        except Exception as e:
                            print(f"处理单篇文章时出错: {str(e)}")
                            continue
                    
                    time.sleep(random.randint(1, 2))
            
            return search_results
                
        except Exception as e:
            print(f"搜索出错: {str(e)}")
            return []

def main():
    crawler = WeChatCrawler()
    
    # 获取文章总数和页数
    total_articles, total_pages = crawler.get_total_articles()
    print(f"总文章数: {total_articles}")
    print(f"总页数: {total_pages}")
    
    # 只爬取第一页进行测试
    crawler.crawl_articles(max_pages=1)  # 修改为只爬取1页

if __name__ == "__main__":
    main() 