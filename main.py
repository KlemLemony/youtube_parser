from googleapiclient.discovery import build # библиотека для взаимодействия с  API YouTube
import time
import csv

from google.colab import drive # финальный файл заливаю себе в облако
drive.mount('/content/gdrive')

from config import api_key, video_Id, path

# напишем функцию, которая преобразует информацию о комментарии, предоставленную в виде объекта snippet, в словарь
def extract_comment_info(comment_id, channel_id, snippet, parent_comment_id=False):
  comment_info = {
      'comment_id': comment_id,
      'parent_id': parent_comment_id,
      'text': snippet['textOriginal'],
      'author': snippet['authorDisplayName'],
      'author_channel_id': snippet['authorChannelId']['value'] if 'authorChannelId' in snippet else False,
      'date': snippet['publishedAt'],
      'likes': snippet['likeCount']
  }
  # определяем, является ли автор комментария владельцем канала
  comment_info['author_comment'] = comment_info['author_channel_id'] and comment_info['author_channel_id'] == channel_id
  return comment_info

# клиент для обращеня к youtube API. Аргумент v3 указывает на версию API, в данном случае на 3 YouTube Data API
service = build('youtube', 'v3', developerKey=api_key)

# Создаем словарь с нужными аргументами для метода commentThreads().list(). Нужен для передачи токена пагинации
args = {
    'videoId': video_Id,
    'part': 'id, snippet, replies',
    'maxResults': 100 # указываем количество возвращаемых айтомов в одном запросе. Айтомс - это массив со сниппетами, в которых находится нужная инфа
}

comments = []

for page in range(0, 100):
  # для задачи нужен метод commentThreads. В методе list, в качестве аргумента, передаем словарь args (то, что мы хотим вернуть)
  r = service.commentThreads().list(**args).execute()

  for top_level in r['items']: # итерируем массив айтемс
    comment_id = top_level['snippet']['topLevelComment']['id']
    snippet = top_level['snippet']['topLevelComment']['snippet'] # получаем экземпляр класса youtube comment
    comments.append(extract_comment_info(comment_id, video_Id, snippet))
    #print(snippet)

    if 'replies' in top_level: # поле с ответами на комменты (может отсутствовать)
      for reply in top_level['replies']['comments']:
        #print(reply)
        comments.append(extract_comment_info(reply['id'], video_Id, reply['snippet'], comment_id))

  args['pageToken'] = r.get('nextPageToken') # метод пагинации нужен для иттерации по всем комментам. В противном случае, зациклимся на первой сотне комментов
  if not args['pageToken']: break # если pageToken не возвращается, то прерываем цикл
  
with open(path, "w+", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter=';')
    for comment in comments:
        writer.writerow(comment.values())