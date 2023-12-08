# Сервис учета посещения сайтов

### Запуск сервиса полностью в docker:
- Сначала создать файл `.env` и скопировать в него содержимое `.env.template`
- Необходимо запустить `docker-compose up`

### Локальная разработка сервиса:
- Устанавливаем библиотеки: `pip install -r requirements.txt`
- Создаем файл `.env` и копируем в него содержимое `.env.local`
- Запускаем `docker-compose up -f docker-compose-local.yml`
- Далее поднимаем приложение с помощью `python manage.py run-server`
- Запускаем тесты с помощью `pytest -vv`

### Пример запросов к сервису:
- **POST запрос**:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8089/api/v1/visited_links/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "links": [
    "https://example.com/"
  ]
}'
```  
- **GET-запрос**:
```bash
curl -X 'GET' \
  'http://0.0.0.0:8089/api/v1/visited_domains/?from_time=0&to_time=10000000000' \
  -H 'accept: application/json'
```