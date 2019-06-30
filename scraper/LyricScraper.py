import os
import requests
import re


class LyricScraper:
    """
    A class that is a template for a scraper object.
    The scraper retrieves lyrics from lyrics.com for the artist specified.
    Member functions write to text files for specified songs or all artist songs.

    """
    artist_name = None

    def __init__(self, name):
        self.artist_name = name

    def get_song_urls(self):
        """
        get_song_urls() parses html data on the main artist page to
        scrape all url's for artist's available songs

        :return: list of url's for all artist songs
        """

        # Get html text from the artist's page
        artist_url = 'https://www.azlyrics.com/' + self.artist_name + "/" + self.artist_name + ".html"
        r = requests.get(artist_url)
        html_string = r.text

        # Parse html text to find song names
        raw_song_urls = re.findall('h:".*html', html_string)
        return_list = []

        # Format song URL's and add to return list
        for page in raw_song_urls:
            return_list.append(page.replace('h:"..', 'https://www.azlyrics.com'))

        return return_list

    @staticmethod
    def write_lyrics(song_url_list):
        """
        write_lyrics() scrapes lyric text from the song_urls provided and writes each url's lyrics to text files
        named 'song_title'.txt in the current working directory.
        Lyrics are processed to remove excess whitespace and page formatting characters
        :param song_url_list: list of song url's to scrape
        :return: void
        """

        for song_url in song_url_list:

            # Get html text from song URL
            r = requests.get(song_url)
            html_string = r.text

            # Parse html text to find beginning and end of lyric text
            start_key = "<!-- Usage of azlyrics.com content by any third-party lyrics provider " \
                        "is prohibited by our licensing agreement. Sorry about that. -->"
            end_key = "<!-- MxM"
            start_pos = html_string.find(start_key) + len(start_key)
            end_pos = html_string.find(end_key)
            raw_lyrics = (html_string[start_pos:end_pos])

            # Remove html tags from the text
            tags = ['<i>', '</i>', '<br>', '</br>', '<div>', '</div>', '&quot;']
            for tag in tags:
                raw_lyrics = raw_lyrics.replace(tag, "")

            # Process the lyrics to remove excess white space and other website formatting
            processed_lyrics = re.sub('\[.*\]', "", raw_lyrics)
            processed_lyrics = re.sub('\([^,)]+?\)', "", processed_lyrics)
            song_name = song_url[song_url.rfind("/") + 1:song_url.rfind(".")]

            # Save lyrics to text file. Catch error for unsupported characters
            f = open(song_name + ".txt", "w+")
            try:
                f.write(processed_lyrics)
            except UnicodeEncodeError:
                print("could not write text file for song " + song_name)
            f.close()

    @staticmethod
    def combine_all_lyrics(path):
        """
        combine_all_lyrics() takes all lyric text files and combines them into a single text file.
        this may be useful for training a model that requires training data to be in a single file.
        :param path: path where the lyric text files are located. If unspecified, cwd is used
        :return: void
        """
        if path is not None:
            absolute = path
        else:
            absolute = os.getcwd()

        # Get list of files in the specified directory
        all_files = os.listdir(absolute)
        total_text = ""

        # Combine all text files into one string
        for f in all_files:
            if f.endswith("*.txt"):
                current = open(absolute + f, 'r')
                total_text += current.read()
                total_text += '\n'
                current.close()

        # Write to new file
        all_lyrics = open(absolute + 'all_lyrics.txt', 'w+')
        s = re.sub("\n\s*\n", "", total_text)
        all_lyrics.write(s)
