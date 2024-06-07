def generate_direct_link(original_link):
    # Extract the FILE_ID from the original Google Drive link
    file_id = original_link.split('/')[-2]
    
    # Construct the direct download link
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return direct_link

# Example usage
shareable_link = "https://drive.google.com/file/d/17_66GS3ONz199-3u1hezAWNQmJW_CZlg/view?usp=sharing"
direct_link = generate_direct_link(shareable_link)
print("Direct download link:", direct_link)