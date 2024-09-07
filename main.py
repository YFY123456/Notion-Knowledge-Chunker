import requests
from bs4 import BeautifulSoup


# List to store all fetched content chunks
chunks = []

def fetch_notion_category_url(base_url):
    """
    Fetch category URLs from the Notion help center.

    Args:
    base_url (str): Base URL of the Notion help center.

    Returns:
    list: List of full URLs for category pages.
    """
    url = base_url
    response = requests.get(url)  # Make a GET request
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content
    guide = soup.find('section', class_='HelpCenterSidebarContent_navSection__fb5g3')  # Find the sidebar section
    links = guide.find_all('a', class_='toggleList_link__safdF')  # Find all category links
    articleLinks = []

    # Extract href attribute and construct full URLs
    for link in links:
        articleLinks.append('https://www.notion.so' + link.get('href'))

    # Filter out URLs that do not start with '/help/category'
    filtered_urls = [url for url in articleLinks if url.startswith('https://www.notion.so/help/category')]
    return filtered_urls

def fetch_article(url):
    """
    Fetch article content from the specified URL.

    Args:
    url (str): URL of the article.

    Returns:
    list: List containing the article's title, introduction, and content.
    """
    response = requests.get(url)  # Make a GET request
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

    # Get the article title
    articleTitle = soup.find('h1', class_='title_title__DWL5N title_titleSizeL__4C9l9 title_titleWeightBold__838EK title_titleFamilyInter__Ra6_Q title_titleColorDark__Pqy5I').get_text()

    # Get the article introduction (if present)
    articleExpress = soup.find('h2', class_='helpArticle_helpArticlePrologueCopy__0cmaN')
    if articleExpress:
        articleExpress = articleExpress.get_text()
    else:
        articleExpress = ''

    title = [articleTitle, articleExpress]  # List of title and introduction

    # Get the article content
    articleContent = soup.find('article', class_='contentfulRichText_richText__rW7Oq contentfulRichText_sans__UVbfz')
    articleDiv = articleContent.find_all(['p', 'a', 'h3'])  # Find all p, a, h3 tags

    articleText = []
    articleText.append(title)  # Add title and introduction to content
    flag = []

    # Process each content block
    for item in articleDiv:
        if item.name == 'a' or item.name == 'h3':
            if flag:
                articleText.append(flag)  # Add previous content block to result
            flag = []  # Reset flag
            flag.append(item.get_text())  # Add new content block
        else:
            flag.append(item.get_text())  # Add regular content

    if flag:
        articleText.append(flag)  # Add the last content block

    return articleText

def fetch_category_content_and_url(url):
    """
    Fetch category content and article links from the specified URL.

    Args:
    url (str): URL of the category.

    Returns:
    dict: Dictionary containing category title, introduction, and all article content.
    """
    response = requests.get(url)  # Make a GET request
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content

    # Get the category title
    header = soup.find('header', class_='_slug__helpCategoryHeroHeader__ggZyi')
    categoryTitle = header.find('h1').get_text()

    # Get the category introduction
    express = soup.find('header', class_='_slug__gridMain__i0wNf _slug__flexColumn__Ltv4T')
    categoryExpress = express.find('h3', class_='title_title__DWL5N title_titleSizeXs__xnVC3 title_titleWeightSemibold__RAo21 title_titleFamilyInter__Ra6_Q').get_text()

    # Initialize category dictionary
    category = {}
    category['title'] = categoryTitle
    category['express'] = categoryExpress
    category['text'] = [[[]]]  # Initialize list for article content

    links = []
    # Find all article links
    articles = soup.find_all("article")
    for article in articles:
        links.append('https://www.notion.so' + article.find('a').get('href'))

    # Fetch content for each article
    for link in links:
        category['text'].append(fetch_article(link))

    return category

# Fetch all category URLs
categoryUrls = fetch_notion_category_url('https://www.notion.so/help')

# Fetch content for each category URL and store in chunks list
for url in categoryUrls:
    chunks.append(fetch_category_content_and_url(url))

# Write the results to output.txt file
with open('output.txt', 'w', encoding='utf-8') as file:
    for i, chunk in enumerate(chunks):
        file.write(f"Chunk {i+1}:\n\n")
        file.write(f"{chunk['title']}\n")
        file.write(f"{chunk['express']}\n")
        for item in chunk['text']:
            for graph in item:
                for sentence in graph:
                    file.write(f"{sentence}\n")
                file.write(f"\n\n")
