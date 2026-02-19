import requests


class AdsApiClient:

    def __init__(self, base_url: str, timeout_s: int = 600):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s


    def list_ad_ids(self, query: str) -> list[str]:
        r = requests.get(f"{self.base_url}/api/v1/links", params={"query": query}, timeout=self.timeout_s)
        r.raise_for_status()
        r = r.json()
        return [r_["url"] for r_ in r]
    

    def get_ad(self, url) -> dict:
        r = requests.get(f"{self.base_url}/api/v1/avto", params={"url": url}, timeout=self.timeout_s)
        r.raise_for_status()
        r = r.json()
        keys = ["title", "url", "photo_urls"]
        out = {
            "description": r["title"],
            "url": r["url"],
            "photos": r["photo_urls"],
            "meta": {k: v for k, v in r.items() if k not in keys}
        }
        return out
    

    def download_photo_bytes(self, url: str) -> bytes:
        r = requests.get(url, timeout=self.timeout_s)
        r.raise_for_status()
        return r.content
    

if __name__ == "__main__":

    base_url = "http://51.250.71.134:8000"
    link = "https://youla.ru/moskva/auto?attributes[term_of_placement][from]=-1%20day&attributes[term_of_placement][to]=now&attributes[sort_field]=date_published"
    api = AdsApiClient(base_url)

    links = api.list_ad_ids(link)

    for l in links:
        res = api.get_ad(l)
        print(res)
