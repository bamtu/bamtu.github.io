from datetime import datetime, timedelta
import os

def create_post(title, category):
    # 현재 시간 KST (+0900)
    now = datetime.utcnow() + timedelta(hours=9)
    date_str = now.strftime("%Y-%m-%d %H:%M:%S +0900")
    filename_date = now.strftime("%Y-%m-%d")

    # 파일 이름 만들기
    slug = title.strip().lower().replace(" ", "-")
    filename = f"{filename_date}-{slug}.md"
    filepath = os.path.join(os.getcwd(), filename)  # 현재 폴더에 생성

    # front matter 작성
    front_matter = f"""---
layout: post
title:  "{title}"
date:   {date_str}
categories: {category}
---
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter)
        print(f"✅ 포스트가 생성되었습니다: {filename}")
    except Exception as e:
        print("❌ 파일 생성 실패:", e)

if __name__ == "__main__":
    print("📝 Jekyll 포스트 생성기\n")
    title = input("포스트 제목: ")
    category = input("카테고리: ")
    create_post(title, category)
