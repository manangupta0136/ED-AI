from flask import Flask, request, jsonify
import yt_dlp # type: ignore

app = Flask(__name__)

# Function to scrape YouTube using yt-dlp
def get_videos(query, max_results=3):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'dump_single_json': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        videos = result.get('entries', [])
        return [
            {
                'title': v.get('title'),
                'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                'thumbnail': v.get('thumbnail')
            }
            for v in videos
        ]

# API endpoint
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    class_level = data.get('class', '')
    subject = data.get('subject', '')
    topic = data.get('topic', '')
    # language = data.get('language', 'english').lower()

    # if language not in ['english', 'hindi']:
    #     return jsonify({"error": "Invalid language. Use 'english'"}), 400

    query = f"{class_level} {subject} {topic} site:youtube.com"
    videos = get_videos(query)
    return jsonify(videos)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
