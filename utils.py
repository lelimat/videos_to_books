# utils.py
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from datetime import datetime
import json
import os
import re
import subprocess
import random
# from langchain.chat_models import ChatOpenAI
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
client = OpenAI()


# chat_model = ChatOpenAI(openai_api_key = OPENAI_API_KEY, model_name='gpt-3.5-turbo', temperature=0.7)

def filter_time(html_list):
    int_list = []
    for elem in html_list:
        if elem == '':
            int_list.append(0)
        else:
            int_list.append(int(elem))
    return int_list


def get_youtube_title(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find('meta', property='og:title')
        if title_tag:
            return title_tag['content']
        else:
            return "Title not found"
    else:
        return "Failed to retrieve page"


# def call_chatgpt(prompt, api_key):
#     openai.api_key = OPENAI_API_KEY

#     response = openai.Completion.create(
#         engine="gpt-3.5-turbo",
#         prompt=prompt,
#         max_tokens=10000
#     )

#     return response.choices[0].text.strip()


def generate_unique_id():

    # Get current date and time
    current_datetime = datetime.now()

    # Format the date and time as a string (e.g., "YYYY-MM-DD HH:MM:SS")
    datetime_string = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    # Generate a random eight-digit number
    random_number = random.randint(10000000, 99999999)

    # Combine date, time, and random number into one string
    combined_string = f"{datetime_string}_{random_number}"

    return combined_string


def is_valid_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=|youtu\.be/)?([^&=%\?]{11})')
    return re.match(youtube_regex, url)


def extract_video_id(url):
    """Extract the YouTube video ID from the URL."""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', # Standard URL
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',                       # Short URL
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',        # Embed URL
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',    # Another Embed URL
        r'(?:https?://)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})'              # Shorts URL
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_playlist_video_ids(playlist_url):
    # Running yt-dlp as a subprocess
    command = ["yt-dlp", "-j", "--flat-playlist", playlist_url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    # Extracting video IDs from the output
    video_ids = []
    for line in out.splitlines():
        video_data = json.loads(line)
        video_ids.append(video_data.get('id'))

    return video_ids


def check_youtube_link(link):
    video_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/watch\?v=[\w-]+'
    playlist_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/playlist\?list=[\w-]+'

    if re.match(video_pattern, link):
        print('video_id', extract_video_id(link))
        return True, [extract_video_id(link)]
    elif re.match(playlist_pattern, link):
        print('video_ids', get_playlist_video_ids(link))
        return True, get_playlist_video_ids(link)
    else:
        return False, "This is not a valid YouTube video link."


def download_youtube_transcript(video_id):

    try:
        # Attempt to download the transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # transcript = transcript_list.find_transcript(['en']).fetch()
        for transcript in transcript_list:
            #transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = transcript_list.find_transcript([transcript.language_code]).fetch()
            print('transcript:', transcript[0]['text'][:100])

            return transcript

        # filtered_transcript = []
        # i = 0
        # entry = transcript[i]
        # while start_seconds <= entry['start'] <= end_seconds and i < len(transcript):
        #     filtered_transcript.append(entry)
        #     i += 1
        #     entry = transcript[i]

        # return filtered_transcript

    except (TranscriptsDisabled, NoTranscriptFound):
        # If no transcript available, use Whisper for transcription
        return f"No transcript found for video {video_id}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_submission(video_id):
    """Save the video ID and the date of submission to a JSON file."""
    data_file = 'pleasetranscribe/data/submissions.json'
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the file exists and read its content, if not create an empty list
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # Append the new submission
    data.append({'video_id': video_id, 'date': current_date})

    # Write the updated data back to the file
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)


# def summarize(text):




def create_chapter(chapter, book_dir, prompt, language='pt'):
    """
    Each chapter has 'number', 'title', 'text'
    """

    # In the future, add other premium features (e.g., remove bad words, use formal or informal language, etc.)
    if language == 'en':
        basic_prompt = f"""Be a book reviewer and text editor to organize the following video transcript as chapters of a book.
        1. Use markdown to write the text.
        2. Modify the text to make it more clear.
        3. Add commas and period when necessary.
        4. Remove repeated words.
        5. Include sub-headers when appropriate in the chapter.
        6. Keep the original language of the text.

        Text:
        """ + chapter['text']
    else:
        basic_prompt = f"""Haja como um editor de livros para organizar essa transcrição de video de uma playlist do YouTube como um capítulo de livro.
        - Adicione pontuação quando necessário.
        - Não resuma o texto.
        - Substitua referências a videos por capítulos, e inscritos por leitores.
        - Use markdown para escrever o texto.
        - Mantenha a língua original, português.

        Texto:
        """ + chapter['text']

    print('prompt:', prompt)
    prompt += f"\n- O número desse capítulo é {chapter['number']}" # Remover??

    basic_prompt = prompt + chapter['text']

    print("chapter['text']", chapter['text'][:100])

    # Calling OpenAI directly
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": basic_prompt},
        ]
    )

    chapter_text = response.choices[0].message.content

    unique_id = generate_unique_id()

    file_prefix = f"Chapter_{chapter['number']:00d}_{chapter['title'].replace(' ', '_')}.md"

    with open(f'{book_dir}/' + file_prefix, 'w') as f:
        f.write(chapter_text)


    return f'{book_dir}/' + file_prefix


def generate_ebook(chapter_files, output_file, ebook_title):

    # Execute the commands
    for book_format in ['html', 'epub', 'docx']: #, 'pdf']:
        # Create a single command to convert all chapters into an ebook
        pandoc_command = ["pandoc", "-o", f"{output_file}.{book_format}", "--metadata", f"title={ebook_title}"] + chapter_files
        try:
            subprocess.run(pandoc_command, check=True)
            print(f"Ebook generated successfully: {output_file}.{book_format}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
            return False

    return True
