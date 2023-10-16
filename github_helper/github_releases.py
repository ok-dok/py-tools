# -*- coding: utf-8 -*-
"""
--------------------------------------------------
    Date Time ：     2023/10/13 17:18
    Author ：        dokeyhou
    IDE ：           PyCharm
    File ：          github_releases.py
    Description:     
--------------------------------------------------
"""
import regex
import requests
from html.parser import HTMLParser


class GithubAssetsPageHtmlParser(HTMLParser):
    asset_urls: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for attr in attrs:
                name, val = attr
                if name == 'href':
                    self.asset_urls.append("https://github.com%s" % val.strip())


def get_github_release_latest_assets(repo_url: str) -> list[str]:
    reg = regex.Regex("^(http[s]?://|git@)github.com[/:]{1}(.*)/(.*)(\\.git)?$")
    matched = reg.match(repo_url)
    if matched and len(matched.groups()) != 4:
        raise Exception("%s is not a valid github repo")
    user = matched.group(2)
    repo = matched.group(3)
    latest_url = f"https://github.com/{user}/{repo}/releases/latest"
    resp = requests.get(latest_url, allow_redirects=False)
    latest_url = resp.headers["location"]
    tag = latest_url.split("tag/")[1]
    assets_url = f"https://github.com/{user}/{repo}/releases/expanded_assets/{tag}"
    resp = requests.get(assets_url)

    parser = GithubAssetsPageHtmlParser()
    parser.feed(resp.text)
    return parser.asset_urls

if __name__ == '__main__':
    repo_url = "https://github.com/matejak/argbash"
    assets = get_github_release_latest_assets(repo_url)
    print(f"Latest release assets of {repo_url}:")
    for asset in assets:
        print(f"- {asset}")
