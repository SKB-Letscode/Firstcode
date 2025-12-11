def search_images_by_bib(image_tags, bib_number):
    """
    Search for images containing a specific bib number.
    Returns a list of image paths.
    """
    results = [img for img, tags in image_tags.items() if bib_number in tags]
    return results

# Example usage
search_number = "1234"
matches = search_images_by_bib(image_tags, search_number)

print(f"Images with bib number {search_number}:")
for match in matches:
    print(match)
