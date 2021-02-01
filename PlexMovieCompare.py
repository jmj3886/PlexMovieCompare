"""
This module is used to traverse a directory structure containing movies in order
to generate a consolidated listing of the movies.
"""

import os
import requests
import json
import xmltodict
import argparse

class CommandLineParser(object):
    """
    This class builds and parses the commandline information given by the user.
    It then organizes that information into usable data to be used by
    the Plex movie comparison tool.
    
    Instance Variables:
        self.parser - The commandline parser which contains the needed flags.
        
    Public Methods:
        parse_info - Parses the passed in arguments against the parser's
                     flags and returns the commandline arguments.
    """
    
    def __init__(self):
        self._arg_parser = argparse.ArgumentParser(
            description="This tool Generates Movie Listings from a Plex "
            "directory and can also compare them for differences between two "
            "Plex servers.",
            conflict_handler="resolve",
        )
        self._arg_parser.add_argument(
            "-c",
            "-C",
            "--compare",
            nargs=2,
            metavar=('serverFile', 'localFile'),
            help="Compares movie listing '<SERVER_FILE>' to '<LOCAL_FILE>' and "
                 "identifies the differences.",
        )
        
    def parse_info(self, args=None):
        """
        This method parses the input arguments, validity checks and returns them.
        
        :param args: The argument string to parse. If Non, the argument
                     strings are taken fro sys.argv.
        :type args: list
        :return: The commandline arguments.
        :rtype: Namespace
        """
        return self._arg_parser.parse_args(args)
        
        
def plex_create_listing():
    extensions = [".mp4", ".avi", ".m4v", ".mkv", ".mov", ".avchd", ".webm"]
    movies = []
    for cur_dir, dirs, files in os.walk("."):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext in extensions:
                movies.append({"title":os.path.splitext(file)[0], "location":os.path.basename(cur_dir)})
                
    with open('PlexMovieListing.txt', 'w') as listing_file:
        for movie in sorted(movies, key=lambda i: i['title']):
            print("%s :- %s" % (movie['title'], movie['location']), file=listing_file)
            
            
def plex_compare(server_listing, local_listing):
    with open('PlexMovieDifferences.txt', 'w') as diff_file:
        server_movies = []
        local_movies = []
        max_location_len = 0
        max_title_len = 0
        with open(server_listing, 'r')as server_file:
            for movie in server_file:
                server_movies.append({'title':movie.split(" :- ")[0], 'location':movie.split(" :- ")[1].strip()})
                if len(server_movies[-1]['title']) > max_title_len:
                    max_title_len = len(server_movies[-1]['title'])
                if len(server_movies[-1]['location']) > max_location_len:
                    max_location_len = len(server_movies[-1]['location'])
        with open(local_listing, 'r')as local_file:
            for movie in local_file:
                local_movies.append({'title':movie.split(" :- ")[0], 'location':movie.split(" :- ")[1].strip()})
                if len(local_movies[-1]['title']) > max_title_len:
                    max_title_len = len(local_movies[-1]['title'])
                if len(local_movies[-1]['location']) > max_location_len:
                    max_location_len = len(local_movies[-1]['location'])
        for server_movie in server_movies:
            difference = True
            title = server_movie['title']
            location = "Move to Plex local at %s" % server_movie['location']
            for local_movie in local_movies:
                if server_movie['title'] == local_movie['title']:
                    difference = False
                    if server_movie['location'] != local_movie['location']:
                        difference = True
                        location = ("%-"+str(max_location_len)+"s -> %s") % (local_movie['location'], server_movie['location'])
            if difference:
                print(("%-"+str(max_title_len)+"s :- %s") % (title, location), file=diff_file)
        for local_movie in local_movies:
            difference = True
            title = local_movie['title']
            location = "Move to Plex server at %s" % local_movie['location']
            for server_movie in server_movies:
                if local_movie['title'] == server_movie['title']:
                    difference = False
            if difference:
                print(("%-"+str(max_title_len)+"s :- %s") % (title, location), file=diff_file)


def get_plex_libraries(plex_address, plex_token):
    libraries = []
    req = requests.get(url = "http://%s:32400/library/sections?X-Plex-Token=%s" % (plex_address, plex_token)) 
    library_json = xmltodict.parse(req.text)
    for folder in library_json["MediaContainer"]["Directory"]:
        if folder["@type"] == "movie":
            libraries.append({"Title":folder["@title"], "Key":folder["@key"]})
    return libraries   


def get_plex_library_content(plex_address, plex_token, libraries):
    for library in libraries:
        req = requests.get(url = "http://%s:32400/library/sections/%s/all?X-Plex-Token=%s" % (plex_address, library["Key"], plex_token)) 
        movies_json = xmltodict.parse(req.text)
        library["Movies"] = []
        for movie in library_json["MediaContainer"]["Video"]:
            library["Movies"].append({"Title":movie})
        with open("Test.txt", "w") as test_file:
            json.dump(xmltodict.parse(req.text), test_file, indent=4)


if __name__ == "__main__":
    args = CommandLineParser().parse_info()
    libraries = get_plex_libraries()
    get_plex_library_content(libraries)
    '''
    if args.compare is not None:
        server_listing, local_listing = args.compare
        plex_compare(server_listing, local_listing)
    else:
        plex_create_listing()
    '''
            
