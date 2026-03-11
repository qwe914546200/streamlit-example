import html
import re
import urllib.parse
from dataclasses import dataclass

import requests
import streamlit as st

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 10


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def _clean_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def search_baidu(query: str, limit: int = 8) -> list[SearchResult]:
    html_text = _fetch_html(f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}")
    pattern = re.compile(
        r'<h3[^>]*>\s*<a[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?(?:<div[^>]*class="[^"]*c-abstract[^"]*"[^>]*>(?P<snippet>.*?)</div>)?',
        re.I | re.S,
    )
    results = []
    for match in pattern.finditer(html_text):
        title = _clean_html(match.group("title"))
        url = html.unescape(match.group("url").strip())
        snippet = _clean_html(match.group("snippet") or "")
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= limit:
            break
    return results


def search_bing(query: str, limit: int = 8) -> list[SearchResult]:
    html_text = _fetch_html(f"https://www.bing.com/search?q={urllib.parse.quote(query)}&setLang=zh-CN")
    pattern = re.compile(
        r'<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>.*?<h2>\s*<a[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>\s*</h2>.*?(?:<p>(?P<snippet>.*?)</p>)?',
        re.I | re.S,
    )
    results = []
    for match in pattern.finditer(html_text):
        title = _clean_html(match.group("title"))
        url = html.unescape(match.group("url").strip())
        snippet = _clean_html(match.group("snippet") or "")
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=snippet))
        if len(results) >= limit:
            break
    return results


def search_google(query: str, limit: int = 8) -> list[SearchResult]:
    html_text = _fetch_html(f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=zh-CN")
    pattern = re.compile(
        r'<a[^>]*href="/url\?q=(?P<url>https?[^&"]+)"[^>]*>\s*<h3[^>]*>(?P<title>.*?)</h3>\s*</a>',
        re.I | re.S,
    )
    results = []
    for match in pattern.finditer(html_text):
        title = _clean_html(match.group("title"))
        url = urllib.parse.unquote(match.group("url").strip())
        if title and url:
            results.append(SearchResult(title=title, url=url, snippet=""))
        if len(results) >= limit:
            break
    return results


SEARCH_ENGINES = {"百度": search_baidu, "必应": search_bing, "Google": search_google}


@st.cache_data(show_spinner=False, ttl=300)
def run_search(engine_name: str, query: str, limit: int) -> list[SearchResult]:
    return SEARCH_ENGINES[engine_name](query, limit=limit)


def render_results(engine_name: str, query: str, limit: int) -> None:
    with st.container(border=True):
        st.subheader(engine_name)
        try:
            results = run_search(engine_name, query, limit)
        except requests.RequestException as exc:
            st.error(f"{engine_name} 请求失败：{exc}")
            return
        except Exception as exc:
            st.error(f"{engine_name} 解析失败：{exc}")
            return

        if not results:
            st.warning("未抓取到结果。可能是反爬限制或页面结构发生变化。")
            return

        for index, item in enumerate(results, start=1):
            st.markdown(f"**{index}. [{item.title}]({item.url})**")
            if item.snippet:
                st.caption(item.snippet)
            st.markdown("---")


st.set_page_config(page_title="三引擎搜索聚合器", layout="wide")
st.title("🔎 浏览器搜索聚合器")
st.write("在一个页面并排查看百度、必应和 Google 的搜索结果，点击标题可直接跳转到新页面。")

with st.sidebar:
    st.header("搜索配置")
    mode = st.radio("搜索模式", ["单引擎", "三引擎同时搜索"], index=1)
    selected_engine = st.selectbox("单引擎选择", list(SEARCH_ENGINES.keys()), index=0)
    limit = st.slider("每个引擎显示结果数", min_value=3, max_value=15, value=8)

query = st.text_input("输入关键词", placeholder="例如：开源 AI Agent 框架")
search_clicked = st.button("开始搜索", type="primary")

if search_clicked and not query.strip():
    st.warning("请输入搜索关键词。")

if search_clicked and query.strip():
    query = query.strip()
    if mode == "单引擎":
        render_results(selected_engine, query, limit)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            render_results("百度", query, limit)
        with col2:
            render_results("必应", query, limit)
        with col3:
            render_results("Google", query, limit)

st.info("提示：Google/Baidu/Bing 可能会在高频请求时触发人机验证，建议适度使用。")
