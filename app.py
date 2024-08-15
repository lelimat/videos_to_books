from flask import Flask, render_template, request, send_file
from utils import (
    create_chapter,
    check_youtube_link,
    download_youtube_transcript,
    get_youtube_title,
    generate_ebook
)
import os
import datetime

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = 'books'

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = ''
    if request.method == 'POST':

        book_title = request.form.get('book_title')
        video_url = request.form.get('video_url')
        prompt = request.form.get('prompt')

        print('video_url', video_url)

        chapters = []
        failed_transcripts = []

    else:
        return render_template('index.html', error='')
        
    if video_url:
        is_valid, video_ids = check_youtube_link(video_url)
        if not is_valid:
            return render_template('index.html', error='Invalid YouTube link: ' + video_url)
        
        for i,video_id in enumerate(video_ids[:4], start=1): # REMOVE [:3] - JUST FOR TESTING!!

            raw_text = ''

            try:
                transcript_parts = download_youtube_transcript(video_id)
                for transcript_part in transcript_parts:
                    raw_text += transcript_part['text'] + ' '
                raw_text += '\n\n'

            except: # (TranscriptsDisabled, NoTranscriptFound):
                failed_transcripts += [video_id]
                # transcript_text = "Transcript not available for this video."
                # return render_template('transcript.html', transcript=transcript_text, video_id=video_id)

            chapters.append(
                {
                    'number': i,
                    'title' : get_youtube_title(video_id),
                    'text' : raw_text,
                }
            )

            # if video_id:
            #     save_submission(video_id)  # Save the video ID and the date
            #     return redirect(url_for('transcript', video_id=video_id))
            

        if chapters:

            book_path = process_chapters(book_title=book_title, chapters=chapters, failed_transcripts=failed_transcripts, prompt=prompt)

            # return redirect(url_for('process_chapters', book_title=book_title, chapters=chapters, failed_transcripts=failed_transcripts))
            return render_template('download_book.html', book_path=book_path)

    return render_template('index.html', error='')


@app.route('/download')
def downloadFile ():
    return send_file(request.args['file_path'], as_attachment=True)


# @app.route('/process_chapters')
def process_chapters(book_title, chapters, failed_transcripts, prompt):

    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    # Create the main directory name
    main_directory = f"{today_date}"

    # Create the subdirectory name with the book title
    sub_directory = os.path.join('books', main_directory, book_title.replace(' ', '_'))

    # Create the directories
    os.makedirs(sub_directory, exist_ok=True)

    chapter_files = []
    for chapter in chapters:
        with open(f"{sub_directory}/raw_text_{chapter['title']}.txt", "w") as f:
            f.write(chapter['text'])

        chapter_file = create_chapter(chapter, sub_directory, prompt)
        chapter_files.append(chapter_file)


    # Create book
    print('Generating ebook')

    if generate_ebook(chapter_files, f"{sub_directory}/{book_title.replace(' ', '_')}", book_title):
        # full_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        book_path=f"{sub_directory}/{book_title.replace(' ', '_')}.docx"
        return book_path
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=43210)
