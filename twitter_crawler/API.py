import json
import argparse
import os
import sys
import subprocess

def write_settings(settings):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Twitter Crawler API Entry")

    parser.add_argument("--cookie", required=True, help="Cookie string")
    parser.add_argument("--filter", required=True, choices=["user", "content"], help="Filter mode: user or content")
    parser.add_argument("--keyword", help="Comma-separated keywords (used when filter=content)")
    parser.add_argument("--username", help="Comma-separated usernames (used when filter=user)")
    parser.add_argument("--start_date", required=True, help="Start date in YYYY-MM-DD")
    parser.add_argument("--end_date", required=True, help="End date in YYYY-MM-DD")
    parser.add_argument("--mode", choices=["text", "media"], help="Download mode (used when filter=content)")
    parser.add_argument("--down_count", type=int, default=50, help="Estimated number of items to download (default: 50), should be multiple of 50")

    args = parser.parse_args()

    # 处理 cookie
    fixed_cookie_tail = " att=1-ytw8qybwMjg98YRu7cRPx9vNXyJA3YOTwLgJjGTK;"
    full_cookie = args.cookie.strip()
    if not full_cookie.endswith(";"):
        full_cookie += ";"
    full_cookie += fixed_cookie_tail

    # 公共设置项
    settings = {
        "cookie": full_cookie,
        "time_range": f"{args.start_date}:{args.end_date}",
        "save_path": os.getcwd()
    }

    if args.filter == "user":
        if not args.username:
            print("Error: --username is required when filter is 'user'")
            sys.exit(1)

        settings.update({
            "user_lst": args.username,
            "has_retweet": False,
            "high_lights": False,
            "likes": False,
            "has_video": True,
            "log_output": False,
            "down_log": False,
            "autoSync": False,
            "image_format": "orig",
            "md_output": False,
            "media_count_limit": 350,
            "proxy": "",
            "max_concurrent_requests": 2
        })

        write_settings(settings)
        subprocess.run([sys.executable, "main.py"])

    elif args.filter == "content":
        if not args.keyword or not args.mode:
            print("Error: --keyword and --mode are required when filter is 'content'")
            sys.exit(1)

        settings.update({
            "keyword": args.keyword.strip(),
            "text_down": True if args.mode == "text" else False,
            "down_count": args.down_count,
        })

        write_settings(settings)
        subprocess.run([sys.executable, "tag_down.py"])

if __name__ == "__main__":
    main()
