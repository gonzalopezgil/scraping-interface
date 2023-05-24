from scrapy.http import HtmlResponse

class NoInternetMiddleware:
    def process_request(self, request, spider):
        return HtmlResponse(url=request.url, body='<html><body><h1>Hello, World!</h1></body></html>', encoding='utf-8')