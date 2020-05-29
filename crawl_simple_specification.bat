@Echo Off

REM docker run -p 8050:8050 scrapinghub/splash
CD "C:\Python\product\product\spiders"
CALL "C:\Python\Python35\python.exe" -m scrapy crawl crawler_specifications_tgdd

TIMEOUT /T 5
scrapy crawl crawler_specifications_viettelstore
TIMEOUT /T 5
scrapy crawl crawler_specifications_dienmaycholon

deactivate