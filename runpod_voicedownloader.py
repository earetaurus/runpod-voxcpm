import argparse
import os
import requests

def download_wav(url, output_dir):
    """Downloads a WAV file from a URL and saves it to a directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Extract filename from URL or use a default
        filename = url.split('/')[-1]
        if not filename.lower().endswith('.wav'):
            filename = 'downloaded_voice.wav'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Successfully downloaded '{filename}' to '{output_dir}'")
        return filepath

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a WAV file from a URL.")
    parser.add_argument("url", help="The URL of the WAV file to download.", nargs='?') # Make URL optional
    args = parser.parse_args()

    output_directory = "./demo/voices"

    if args.url: # Only proceed if a URL was provided
        download_wav(args.url, output_directory)
    else:
        print("No URL provided. Exiting.")
