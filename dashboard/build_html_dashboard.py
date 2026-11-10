"""
Builds the standalone and artifact HTML IEEE Research Paper Dashboard.
"""
import os

with open("dashboard/template.html", "r", encoding="utf-8") as f:
    template = f.read()

with open("dashboard/data.json", "r", encoding="utf-8") as f:
    data_json = f.read()

html_content = template.replace("<!-- DATA_JSON_PLACEHOLDER -->", data_json)

# Save to dashboard/index.html
with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Save to artifact directory
artifact_dir = r"C:\Users\Spidey\.gemini\antigravity\brain\1e8668a3-0333-45fc-ab6b-6b4dd770c84a"
os.makedirs(artifact_dir, exist_ok=True)
artifact_path = os.path.join(artifact_dir, "ieee_research_paper_dashboard.html")
with open(artifact_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated dashboard/index.html ({len(html_content)} bytes)")
print(f"Generated artifact dashboard at: {artifact_path}")
