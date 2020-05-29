@Echo Off
rem START cmd.exe /C "D:\Luanvan\xampp_start.exe"

rem START cmd.exe /C "C:\Program Files\Docker\Docker\Docker Desktop.exe"
rem taskkill /IM cmd.exe
rem TIMEOUT /T 60
rem START cmd.exe /C docker run -p 8050:8050 scrapinghub/splash
rem taskkill /IM cmd.exe

TIMEOUT /T 10
CD cmd.exe "C:\Python\product\product\spiders"

CALL cmd.exe /C "C:\Python\Python35\python.exe" -m scrapy crawl crawler_reviews_tgdd

scrapy crawl crawler_reviews_fpt

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