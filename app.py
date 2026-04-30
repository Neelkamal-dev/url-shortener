from flask import Flask, request, jsonify, redirect, render_template, abort
from database import init_db, get_db, close_db
from url_service import create_short_url, get_original_url, get_all_urls, get_url_stats
import os

app = Flask(__name__)
app.teardown_appcontext(close_db)

with app.app_context():
    init_db()


def get_base_url():
    return os.environ.get('BASE_URL', request.host_url.rstrip('/'))


@app.route('/')
def index():
    return render_template('index.html', base_url=get_base_url())


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    original_url = data['url'].strip()
    custom_code = data.get('custom_code', '').strip() or None

    if not original_url:
        return jsonify({'error': 'URL cannot be empty'}), 400

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    db = get_db()
    result = create_short_url(db, original_url, custom_code)

    if 'error' in result:
        return jsonify(result), 400

    result['short_url'] = f"{get_base_url()}/{result['short_code']}"
    return jsonify(result), 201


@app.route('/api/urls', methods=['GET'])
def list_urls():
    db = get_db()
    urls = get_all_urls(db)
    for url in urls:
        url['short_url'] = f"{get_base_url()}/{url['short_code']}"
        # Convert datetime to string for JSON
        for key in ('created_at', 'last_accessed'):
            if url.get(key):
                url[key] = str(url[key])
    return jsonify({'urls': urls, 'total': len(urls)})


@app.route('/api/stats/<short_code>', methods=['GET'])
def url_stats(short_code):
    db = get_db()
    stats = get_url_stats(db, short_code)
    if not stats:
        return jsonify({'error': 'Short URL not found'}), 404
    stats['short_url'] = f"{get_base_url()}/{short_code}"
    for key in ('created_at', 'last_accessed'):
        if stats.get(key):
            stats[key] = str(stats[key])
    return jsonify(stats)


@app.route('/api/urls/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    from sqlalchemy import text
    db = get_db()
    result = db.execute(text('DELETE FROM urls WHERE short_code = :code'), {'code': short_code})
    db.commit()
    if result.rowcount == 0:
        return jsonify({'error': 'Short URL not found'}), 404
    return jsonify({'message': 'URL deleted successfully'})


@app.route('/<short_code>')
def redirect_url(short_code):
    db = get_db()
    original_url = get_original_url(db, short_code)
    if not original_url:
        abort(404)
    return redirect(original_url, code=302)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
