@Echo Off
rem START cmd.exe /C "D:\Luanvan\xampp_start.exe"

rem START cmd.exe /C "C:\Program Files\Docker\Docker\Docker Desktop.exe"
rem taskkill /IM cmd.exe
rem TIMEOUT /T 60
rem START cmd.exe /C docker run -p 8050:8050 scrapinghub/splash
rem taskkill /IM cmd.exe


CD cmd.exe "C:\Python\product\product\spiders"

CALL cmd.exe /C "C:\Python\Python35\python.exe" -m scrapy crawl crawler_product_tgdd

TIMEOUT /T 5
scrapy crawl crawler_product_viettelstore
TIMEOUT /T 5
scrapy crawl crawler_product_fpt
TIMEOUT /T 5
scrapy crawl crawler_product_hoanghamobile
TIMEOUT /T 5
scrapy crawl crawler_product_dienmaycholon
TIMEOUT /T 5
scrapy crawl crawler_product_cellphoneS
TIMEOUT /T 5
REM scrapy crawl crawler_reviews_tgdd
REM TIMEOUT /T 5
REM scrapy crawl crawler_reviews_fpt
REM TIMEOUT /T 5
rem START cmd.exe /C "D:\Luanvan\xampp_stop.exe"
rem TIMEOUT /T 10
rem taskkill /IM cmd.exe
rem TIMEOUT /T 30

rem taskkill /IM cmd.exe
exit

deactivate