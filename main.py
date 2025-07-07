from aha_api import AhaAPI
from rich import print
from rich.console import Console
from rich.table import Table
import os
import openai


def groom_features(features):
    groomed = []
    for feat in features:
        name = feat.get('name', '')
        desc = feat.get('description', '') or ''
        summary = (desc[:60] + '...') if len(desc) > 60 else desc
        # Categorize by status or keyword
        status = feat.get('workflow_status', {}).get('name', '')
        if 'bug' in name.lower() or 'bug' in desc.lower():
            category = 'Bug'
        elif 'feature' in name.lower() or 'feature' in desc.lower():
            category = 'Feature'
        else:
            category = 'Other'
        # Prioritize by keyword
        if any(word in name.lower() + desc.lower() for word in ['urgent', 'high', 'critical']):
            priority = 'High'
        elif any(word in name.lower() + desc.lower() for word in ['medium', 'normal']):
            priority = 'Medium'
        else:
            priority = 'Low'
        groomed.append({
            'id': feat.get('id'),
            'name': name,
            'summary': summary,
            'category': category,
            'priority': priority,
            'status': status
        })
    return groomed

def generate_product_summary(features):
    # Combine all names and descriptions
    all_text = ' '.join([
        f["name"] + " " + (f.get("description", "") or "")
        for f in features
    ])
    # Simple summary: show most common words (excluding stopwords)
    from collections import Counter
    import re
    stopwords = set([
        'the', 'and', 'for', 'with', 'that', 'this', 'from', 'are', 'but', 'not', 'have', 'has', 'was', 'you', 'your', 'all', 'can', 'will', 'our', 'their', 'they', 'them', 'which', 'when', 'what', 'how', 'who', 'where', 'why', 'about', 'into', 'more', 'than', 'also', 'any', 'each', 'other', 'use', 'used', 'using', 'should', 'could', 'would', 'may', 'might', 'must', 'shall', 'being', 'been', 'were', 'had', 'did', 'does', 'doing', 'on', 'in', 'at', 'by', 'to', 'of', 'as', 'is', 'it', 'if', 'or', 'an', 'a', 'be', 'so', 'we', 'i', 'he', 'she', 'his', 'her', 'its', 'my', 'me', 'do', 'up', 'out', 'no', 'yes', 'just', 'now', 'new', 'get', 'got', 'make', 'made', 'see', 'seen', 'go', 'went', 'back', 'off', 'over', 'under', 'again', 'still', 'even', 'very', 'much', 'such', 'like', 'one', 'two', 'three', 'first', 'last', 'next', 'previous', 'current', 'future', 'past', 'before', 'after', 'since', 'because', 'due', 'per', 'via', 'etc', 'etc.', 'eg', 'e.g.', 'ie', 'i.e.'
    ])
    words = re.findall(r'\b\w{4,}\b', all_text.lower())
    keywords = [w for w in words if w not in stopwords]
    common = Counter(keywords).most_common(10)
    summary = ', '.join([f"{word} ({count})" for word, count in common])
    return summary

def generate_openai_summary(features):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    client = openai.OpenAI(api_key=api_key)
    # Prepare the text for summarization
    story_texts = [
        f"- {f['name']}: {f.get('description', '') or ''}" for f in features
    ]
    prompt = (
        "You are a product manager assistant. Given the following list of product stories, "
        "write a concise summary (3-5 sentences) describing what the product is, its main modules, and its current focus.\n\n"
        + '\n'.join(story_texts)
        + "\n\nSummary:"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"[OpenAI error: {e}]"

def main():
    console = Console()
    base_url = input('Enter your Aha! base URL (e.g., https://yourcompany.aha.io): ').strip()
    product_id = input('Enter your Aha! product ID: ').strip()

    api = AhaAPI(base_url)
    console.print(f"[bold green]Fetching features for product:[/bold green] {product_id}")
    try:
        data = api.fetch_features(product_id)
        features = data.get('features', [])
        # Debug: Print raw features from API
        print("\n[DEBUG] Raw features from Aha! API:")
        from rich.pretty import pprint
        pprint(features)
        groomed = groom_features(features)
        table = Table(title="Groomed Aha! Features")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Summary", style="yellow")
        table.add_column("Category", style="blue")
        table.add_column("Priority", style="red")
        table.add_column("Status", style="green")
        for feat in groomed:
            table.add_row(str(feat['id']), feat['name'], feat['summary'], feat['category'], feat['priority'], feat['status'])
        console.print(table)
        # Try OpenAI summary first
        ai_summary = generate_openai_summary(features)
        if ai_summary:
            console.print(f"\n[bold blue]AI Product Summary:[/bold blue] {ai_summary}")
        else:
            summary = generate_product_summary(features)
            console.print(f"\n[bold blue]Product Summary (Top Keywords):[/bold blue] {summary}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main() 