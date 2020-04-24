@Echo Off
START cmd.exe /C "D:\Luanvan\xampp_start.exe"

START cmd.exe /C "C:\Program Files\Docker\Docker\Docker Desktop.exe"
taskkill /IM cmd.exe
TIMEOUT /T 60
START cmd.exe /C docker run -p 8050:8050 scrapinghub/splash
taskkill /IM cmd.exe

TIMEOUT /T 10
CD cmd.exe "C:\Python\product\product\spiders"

CALL cmd.exe /C "C:\Python\Python35\python.exe" -m scrapy crawl crawler_product_tgdd

REM TIMEOUT /T 5
REM scrapy crawl crawler_product_viettelstore
REM TIMEOUT /T 5
REM scrapy crawl crawler_product_fpt
REM TIMEOUT /T 5
REM scrapy crawl crawler_product_cellphoneS
REM TIMEOUT /T 5
REM scrapy crawl crawler_product_hoanghamobile
REM TIMEOUT /T 5
REM scrapy crawl crawler_product_dienmaycholon
REM TIMEOUT /T 5
REM scrapy crawl crawler_reviews_tgdd
REM TIMEOUT /T 5
REM scrapy crawl crawler_reviews_fpt
REM TIMEOUT /T 5
START cmd.exe /C "D:\Luanvan\xampp_stop.exe"
TIMEOUT /T 10
taskkill /IM cmd.exe
TIMEOUT /T 30

taskkill /IM cmd.exe
exit

deactivate