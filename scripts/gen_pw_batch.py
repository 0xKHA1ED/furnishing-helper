import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
batch = json.loads((root / "data/appliances/_batch_next.json").read_text(encoding="utf-8"))
urls_js = json.dumps(batch)
code = f"""async (page) => {{
  const urls = {urls_js};
  const results = {{}};
  for (const url of urls) {{
    try {{
      await page.goto(url, {{ waitUntil: 'domcontentloaded', timeout: 45000 }});
      await page.waitForTimeout(300);
      const data = await page.evaluate(() => {{
        const og = document.querySelector('meta[property="og:image"]')?.content || null;
        const gallery = [...new Set([...document.querySelectorAll('img')]
          .map(i => i.src || i.currentSrc)
          .filter(s => s && s.includes('cloudfront') && /\\.(jpe?g|png|webp)/i.test(s)))].slice(0, 12);
        return {{ og, gallery }};
      }});
      results[url] = data;
    }} catch (e) {{
      results[url] = {{ og: null, gallery: [], error: String(e.message || e) }};
    }}
  }}
  return results;
}}"""
(root / "scripts/_pw_batch.js").write_text(code, encoding="utf-8")
print("wrote", len(batch), "urls")
