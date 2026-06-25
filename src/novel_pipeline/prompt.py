def prompt_user(chapter_num: int, draft_text: str) -> bool:
    print(f"Chapter {chapter_num} draft (first 500 chars):\n{draft_text[:500]}\n")
    choice = input("[y/n/q]: ").strip().lower()
    if choice == "q":
        raise KeyboardInterrupt
    return choice == "y"
