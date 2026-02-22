import json
import os
from pathlib import Path
from html import escape
import re

# Collect all questions
questions_by_exam = {}
pa_dump_path = Path(".")

for exam_dir in sorted(pa_dump_path.iterdir()):
    if not exam_dir.is_dir():
        continue

    exam_name = exam_dir.name
    questions = []

    for json_file in sorted(exam_dir.glob("*.json"), key=lambda x: int(x.stem)):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                question_html = data.get('question', '')
                difficulty = data.get('difficulty', 'unknown')
                questions.append({
                    'number': json_file.stem,
                    'html': question_html,
                    'difficulty': difficulty
                })
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    if questions:
        questions_by_exam[exam_name] = questions

# Generate HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programming Exam Questions</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
            background: #fff;
            padding: 15px;
            border-left: 4px solid #2196F3;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .question-item {
            background: white;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .question-header {
            padding: 15px;
            cursor: pointer;
            user-select: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fafafa;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }
        .question-header:hover {
            background: #f0f0f0;
        }
        .question-title {
            font-weight: bold;
            color: #333;
            flex-grow: 1;
        }
        .difficulty {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        .difficulty.easy {
            background: #4CAF50;
            color: white;
        }
        .difficulty.medium {
            background: #FF9800;
            color: white;
        }
        .difficulty.hard {
            background: #F44336;
            color: white;
        }
        .difficulty.unknown {
            background: #9E9E9E;
            color: white;
        }
        .question-preview {
            padding: 0 15px 15px 15px;
            max-height: 60px;
            overflow: hidden;
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        .question-content {
            padding: 20px;
            display: none;
            border-top: 1px solid #eee;
        }
        .question-item.expanded .question-content {
            display: block;
        }
        .question-item.expanded .question-preview {
            display: none;
        }
        .expand-icon {
            margin-left: 10px;
            transition: transform 0.3s;
            font-size: 20px;
            color: #666;
        }
        .question-item.expanded .expand-icon {
            transform: rotate(180deg);
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>Programming Exam Questions</h1>
"""

for exam_name, questions in sorted(questions_by_exam.items()):
    html += f'    <h2>{exam_name}</h2>\n'

    for q in questions:
        # Create a text preview (strip HTML tags for preview)
        preview_text = re.sub('<[^<]+?>', '', q['html'])[:200].strip()

        html += f'''    <div class="question-item" onclick="this.classList.toggle('expanded')">
        <div class="question-header">
            <div class="question-title">
                Question {q['number']}
                <span class="difficulty {q['difficulty']}">{q['difficulty'].upper()}</span>
            </div>
            <span class="expand-icon">▼</span>
        </div>
        <div class="question-preview">{escape(preview_text)}...</div>
        <div class="question-content">
{q['html']}
        </div>
    </div>
'''

html += """</body>
</html>"""

# Write HTML file
with open('all_questions.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Generated all_questions.html with {len(questions_by_exam)} exams")
for exam, qs in sorted(questions_by_exam.items()):
    print(f"  {exam}: {len(qs)} questions")
