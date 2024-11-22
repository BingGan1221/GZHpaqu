import streamlit as st
import pandas as pd
from wechat_crawler import WeChatCrawler
import time

# 设置页面标题
st.set_page_config(page_title="微信公众号文章爬取", layout="wide")

# 公众号配置
ACCOUNTS = {
    "32号": {"fakeid": "MzIwMTE4MzYzNg==", "token": "11845441"},
    "稻草人旅行": {"fakeid": "MjM5MTA5NjAyMA==", "token": "11845441"},
    "游侠客": {"fakeid": "MjM5NTgxNjU0MQ==", "token": "11845441"},
    "VIVA旅行家": {"fakeid": "MjM5MjQ4MzMwMA==", "token": "11845441"},
    "走之旅行": {"fakeid": "MzkxNDI3MTY1OA==", "token": "11845441"},
    "行走20岁": {"fakeid": "MzAwODE3MTgyNg==", "token": "11845441"}
}

def main():
    st.title("微信公众号文章爬取工具")
    
    # 选择功能
    task = st.sidebar.selectbox(
        "选择功能",
        ["批量爬取", "关键词搜索"]
    )
    
    # 选择公众号
    account_name = st.selectbox(
        "选择公众号",
        list(ACCOUNTS.keys())
    )
    
    if account_name:
        crawler = WeChatCrawler()
        crawler.account_name = account_name
        crawler.data['fakeid'] = ACCOUNTS[account_name]['fakeid']
        crawler.data['token'] = ACCOUNTS[account_name]['token']
        
        if task == "批量爬取":
            crawl_articles(crawler)
        else:
            search_articles(crawler)

def crawl_articles(crawler):
    try:
        # 获取总文章数
        total_articles, _ = crawler.get_total_articles()
        st.info(f"该公众号共有 {total_articles} 篇文章")
        
        # 输入要爬取的文章数
        article_count = st.number_input(
            "要爬取的文章数",
            min_value=1,
            max_value=total_articles,
            value=min(100, total_articles)
        )
        
        if st.button("开始爬取"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 计算需要爬取的页数
            pages_needed = (article_count + 4) // 5
            
            # 开始爬取
            results = []
            for i, data in enumerate(crawler.crawl_articles(max_pages=pages_needed, target_count=article_count)):
                progress = min(1.0, (i + 1) / pages_needed)
                progress_bar.progress(progress)
                status_text.text(f"正在爬取第 {i+1}/{pages_needed} 页...")
                results.extend(data)
            
            # 转换为DataFrame并显示
            if results:
                df = pd.DataFrame(results, columns=['标题', '链接', '发布时间'])
                st.dataframe(df)
                
                # 提供下载链接
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "下载CSV文件",
                    csv,
                    f"{crawler.account_name}_articles.csv",
                    "text/csv",
                    key='download-csv'
                )
            
            st.success("爬取完成！")
            
    except Exception as e:
        st.error(f"爬取失败: {str(e)}")

def search_articles(crawler):
    keyword = st.text_input("输入搜索关键词")
    
    if keyword and st.button("搜索"):
        try:
            with st.spinner('正在搜索...'):
                results = crawler.search_articles(keyword)
            
            if results:
                st.write(f"找到 {len(results)} 篇相关文章：")
                for article in results:
                    with st.expander(article['title']):
                        st.write(f"发布时间: {article['create_time']}")
                        st.write(f"文章链接: {article['link']}")
            else:
                st.info("没有找到相关文章")
                
        except Exception as e:
            st.error(f"搜索失败: {str(e)}")

if __name__ == "__main__":
    main() 