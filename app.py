from flask import Flask, render_template, request, send_file, jsonify
from wechat_crawler import WeChatCrawler
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/check_total', methods=['POST'])
def check_total():
    try:
        fakeid = request.form.get('fakeid')
        token = request.form.get('token')
        
        crawler = WeChatCrawler()
        crawler.data['fakeid'] = fakeid
        crawler.data['token'] = token
        
        total_articles, _ = crawler.get_total_articles()
        return jsonify({'total_count': total_articles})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        fakeid = request.form.get('fakeid')
        token = request.form.get('token')
        account_name = request.form.get('account_name')
        article_count = int(request.form.get('article_count', 100))
        
        crawler = WeChatCrawler()
        crawler.account_name = account_name
        crawler.data['fakeid'] = fakeid
        crawler.data['token'] = token
        
        # 计算需要爬取的页数
        pages_needed = (article_count + 4) // 5  # 向上取整
        crawler.crawl_articles(max_pages=pages_needed, target_count=article_count)
        
        filename = f"{account_name}.csv"
        
        # 返回成功信息和文件名
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'成功爬取 {article_count} 篇文章'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        return send_file(
            file_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/search', methods=['POST'])
def search():
    try:
        keyword = request.form.get('keyword')
        fakeid = request.form.get('fakeid')
        token = request.form.get('token')
        account_name = request.form.get('account_name')
        
        if not keyword:
            return jsonify({'error': '请输入搜索关键词'}), 400
            
        crawler = WeChatCrawler()
        crawler.account_name = account_name
        crawler.data['fakeid'] = fakeid
        crawler.data['token'] = token
        
        # 搜索文章
        results = crawler.search_articles(keyword)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 