import asyncio
from typing import List
from crawl4ai import *
import json

async def simple_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.msn.com/en-ca/news/world/ukraine-war-latest-third-round-of-ukraine-russia-peace-talks-set-for-july-23-zelensky-says/ar-AA1J15yW",
        )
        print(result.markdown)

urls=[  
        "https://openai.com/api/pricing",
        "https://help.openai.com/en/articles/11752874-chatgpt-agent"
    ]

async def parallel_crawl():
    async with AsyncWebCrawler() as crawler:
        results: List[CrawlResult] = await crawler.arun_many(
            urls=urls
        )
        print(results.success)

async def fit_markdown():
    async with AsyncWebCrawler() as crawler:
        result: CrawlResult = await crawler.arun(
            # Benzinga - url = "https://www.benzinga.com/markets/macro-economic-events/25/07/46491573/waller-fed-chair-trump-rate-cut-july",
            #Bloomberg - url = "https://www.bloomberg.com/news/articles/2025-07-19/china-s-inaction-deepens-peril-for-struggling-property-stocks?srnd=homepage-asia",
            # url= "https://timesofindia.indiatimes.com/world/us/jets-were-shot-down-donald-trump-says-stopped-a-lot-of-wars-again-brings-up-india-pakistan-conflict/articleshow/122775960.cms",
            # url="https://www.newindianexpress.com/world/2025/Jul/19/israel-syria-leaders-agree-on-ceasefire-us-envoy",
            # url = "https://edition.cnn.com/2025/07/18/middleeast/israel-syria-ceasefire-latam-intl",
            # url = "https://www.bbc.com/news/articles/c23g5xpggzmo",
            url = "https://www.msn.com/en-ca/news/world/ukraine-war-latest-third-round-of-ukraine-russia-peace-talks-set-for-july-23-zelensky-says/ar-AA1J15yW",
            config=CrawlerRunConfig(
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter()
                )
            )
        )

    print(result.markdown)

async def media_link():
    async with AsyncWebCrawler() as crawler:
        result: List[CrawlResult] = await crawler.arun("https://www.bbc.com/news/articles/c23g5xpggzmo")

        internal_links = result.links.get("internal", [])
        external_links = result.links.get("external", [])
        print(f"Found {len(internal_links)} internal links.")
        print(f"Found {len(internal_links)} external links.")
        print(f"Found {len(result.media)} media items.")
        print(internal_links[1])
        print(external_links[1])
        
        images_info = result.media.get("images", [])
        print(f"Found {len(images_info)} images in total.")
        for i, img in enumerate(images_info[:3]):  # Inspect just the first 3
            print(f"[Image {i}] URL: {img['src']}")

async def Llm_structed_extraction_no_schema():

    deep_crawler = BestFirstCrawlingStrategy(
        max_depth=5, max_pages=5
    )

    # config1=CrawlerRunConfig(
    #             markdown_generator=JsonCssExtractionStrategy(
    #                 content_filter=PruningContentFilter()
    #             )
    #         )

    extraction_stragy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="groq/meta-llama/llama-4-scout-17b-16e-instruct",
            api_token="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"
        ),
        instruction="extract all the latest news present in this url and extract each news article: title, full description with minimum 200 words, date, time and url from the news url",
        extraction_type="schema",
        schema={
        "title": "string",
        "description": "string",
        "url": "string",
        "date": "string",
        "time": "string"
        },
        verbose=True
    )

    schema={
        "title": "string",
        "description": "string",
        "url": "string",
        "date": "string",
        "time": "string"
    }
        
    config2 = CrawlerRunConfig(deep_crawl_strategy=deep_crawler)

    async with AsyncWebCrawler() as crawler:
        results: List[CrawlResult] = await crawler.arun(
        "https://www.benzinga.com/recent",config=config2 
    )

    print(results)
    for result in results:
        print(f"Cleaned_HTML: {result.cleaned_html}")
        print(f"URL: {result.url}")
        print(f"Success: {result.success}")
        print(f"Content: {result.extracted_content}")
        # if result.success:
        #     data = json.loads(result.extracted_content)
        #     print(json.dumps(data, indent=2))
        # else:
        #     print("Failed to extract structured data")

if __name__ == "__main__":
    # asyncio.run(simple_crawl())
    # asyncio.run(parallel_crawl())
    # asyncio.run(fit_markdown())
    # asyncio.run(media_link())
    asyncio.run(Llm_structed_extraction_no_schema())