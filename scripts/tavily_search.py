#!/usr/bin/env python3
"""
搜神猎手 (SouShen Hunter) - Tavily 搜索引擎
使用 Tavily REST API，无需浏览器自动化
"""

import json
import sys
import os
from typing import List, Optional
from dataclasses import dataclass, asdict

try:
    from tavily import TavilyClient
except ImportError:
    print(json.dumps({"error": "tavily-python not installed. Run: pip install tavily-python"}, ensure_ascii=False))
    sys.exit(1)


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str
    url: str
    snippet: str
    source: str
    result_type: str = "organic"


class TavilySearchAgent:
    """Tavily 搜索代理 - API 模式，无需浏览器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('TAVILY_API_KEY')
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required. Get your key at https://app.tavily.com")
        self.client = TavilyClient(api_key=self.api_key)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """执行 Tavily 搜索并返回结构化结果"""
        results = []

        response = self.client.search(
            query=query,
            max_results=num_results,
            search_depth="basic",
        )

        for item in response.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                source=item.get("url", "").split("/")[2] if item.get("url", "").startswith("http") else "",
                result_type="organic"
            ))

        return results[:num_results]


def format_output(results: List[SearchResult]) -> str:
    """格式化输出为JSON"""
    return json.dumps({
        "tool": "soushen-hunter",
        "mode": "tavily_search",
        "total": len(results),
        "results": [asdict(r) for r in results]
    }, ensure_ascii=False, indent=2)


def parse_args():
    """解析命令行参数"""
    args = sys.argv[1:]
    result = {
        'mode': None,
        'query': None,
        'num_results': 10
    }

    if '--num' in args:
        idx = args.index('--num')
        if idx + 1 < len(args):
            try:
                result['num_results'] = int(args[idx + 1])
                args.pop(idx + 1)
                args.pop(idx)
            except ValueError:
                pass

    if len(args) < 1:
        return None

    result['mode'] = 'search'
    result['query'] = args[0]
    return result


async def main():
    """主函数 - CLI 入口"""
    parsed = parse_args()

    if parsed is None:
        help_text = {
            "tool": "soushen-hunter-tavily",
            "usage": {
                "search": "python tavily_search.py <query> [--num N]"
            },
            "options": {
                "--num": "搜索结果数量 (默认 10)"
            },
            "examples": [
                "python tavily_search.py 'OpenClaw AI'",
                "python tavily_search.py 'AI' --num 20"
            ],
            "env": {
                "TAVILY_API_KEY": "Tavily API 密钥 (必须)"
            }
        }
        print(json.dumps(help_text, ensure_ascii=False, indent=2))
        sys.exit(1)

    agent = TavilySearchAgent()
    results = await agent.search(parsed['query'], num_results=parsed['num_results'])
    print(format_output(results))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
