def resolve_category(user_text, categories: dict):
    if not user_text:
        return []

    text = user_text.lower()
    matches = []

    for category_type, group in categories.items():
        for key, label in group.items():
            if label.lower() in text:
                matches.append(key)

    return list(set(matches))






# def resolve_category(user_text: str, categories: dict):
#     matches = []

#     for group in categories.values():
#         for key, label in group.items():
#             if label.lower() in user_text.lower():
#                 matches.append(key)

#     return list(set(matches))


