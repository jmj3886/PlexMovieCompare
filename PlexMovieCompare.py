"""
This module is used to find and compare the libraries in Plex servers.
The module can be used to generate listing files for comparison, 
compare listing files, and compare raw Plex library results.
"""

import sys
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
            "directory and compares them for differences between two "
            "Plex servers.",
            conflict_handler="resolve",
        )
        self._arg_parser.add_argument(
            "--listing_file",
            nargs=1,
            type=str,
            metavar="<REMOTE_MOVIE_LISTING>",
            help="The movie listing file generated remotely for "
            "comparison.",
        )
        self._arg_parser.add_argument(
            "--local_address",
            nargs=1,
            type=str,
            metavar="<LOCAL_SERVER_ADDRESS>",
            help="The IP address of the local Plex server.",
        )
        self._arg_parser.add_argument(
            "--api_token",
            nargs=1,
            type=str,
            metavar="<API_TOKEN>",
            help="The API token for connecting to Plex Web API.",
        )
        self._arg_parser.add_argument(
            "-c",
            "-C",
            "--compare",
            metavar=('<REMOTE_SERVER_LISTING>', '<LOCAL_SERVER_LISTING>'),
            help="Compares movie listings '<REMOTE_SERVER_LISTING>' to '<LOCAL_SERVER_LISTING>' and "
                 "identifies the differences. If <LOCAL_SERVER_LISTING> is not given, "
                 "--local_address and --api_token should be given to create the listing in memory.",
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


def plex_compare(remote_listing, local_listing):
    with open("PlexMovieDifferences.txt", "w") as diff_file:
        max_location_len = 0
        max_title_len = 0
        for movie in remote_listing:
            if len(movie["Title"]) > max_title_len:
                max_title_len = len(movie["Title"])
            if len(movie["Library"]) > max_location_len:
                max_location_len = len(movie["Library"])
        for movie in local_listing:
            if len(movie["Title"]) > max_title_len:
                max_title_len = len(movie["Title"])
            if len(movie["Library"]) > max_location_len:
                max_location_len = len(movie["Library"])
        for server_movie in remote_listing:
            difference = True
            title = server_movie["Title"]
            location = "Move to Plex local at %s" % server_movie["Library"]
            for local_movie in local_listing:
                if server_movie["Title"] == local_movie["Title"]:
                    difference = False
                    if server_movie["Library"] != local_movie["Library"]:
                        difference = True
                        location = ("%-" + str(max_location_len) + "s -> %s") % (
                            local_movie["Library"],
                            server_movie["Library"],
                        )
            if difference:
                print(
                    ("%-" + str(max_title_len) + "s :- %s") % (title, location),
                    file=diff_file,
                )
        for local_movie in local_listing:
            difference = True
            title = local_movie["Title"]
            location = "Move to Plex server at %s" % local_movie["Library"]
            for server_movie in remote_listing:
                if local_movie["Title"] == server_movie["Title"]:
                    difference = False
            if difference:
                print(
                    ("%-" + str(max_title_len) + "s :- %s") % (title, location),
                    file=diff_file,
                )


def get_plex_libraries(plex_address, plex_token):
    libraries = []
    print("http://%s/library/sections?X-Plex-Token=%s"
        % (plex_address, plex_token))
    req = requests.get(
        url="http://%s/library/sections?X-Plex-Token=%s"
        % (plex_address, plex_token)
    )
    print(req)
    library_json = xmltodict.parse(req.text)
    json.dumps(library_json, indent=4)
    for folder in library_json["MediaContainer"]["Directory"]:
        if folder["@type"] == "movie":
            libraries.append({"Title": folder["@title"], "Key": folder["@key"]})
    return libraries


def get_plex_library_content(plex_address, plex_token, libraries):
    for library in libraries:
        req = requests.get(
            url="http://%s/library/sections/%s/all?X-Plex-Token=%s"
            % (plex_address, library["Key"], plex_token)
        )
        movies_json = xmltodict.parse(req.text)
        library["Movies"] = []
        for movie in movies_json["MediaContainer"]["Video"]:
            library["Movies"].append({"Title": movie["@title"]})


def generate_movie_listing(local_address, plex_token):
    listing = []
    libraries = get_plex_libraries(local_address, plex_token)
    get_plex_library_content(local_address, plex_token, libraries)
    
    for library in libraries:
        for movie in library["Movies"]:
            listing.append({"Title": movie["Title"], "Library": library["Title"]})
    return listing


if __name__ == "__main__":
    args = CommandLineParser().parse_info()
    if args.compare is not None:
        with open(args.compare[0], 'r') as listing_file:
          remote_listing = json.load(listing_file)
        if len(args.compare) < 2 or args.compare[1] is None:
            if (("local_address" in dir(args)) and ("api_token" in dir(args)) and (args.local_address is not None) and (args.api_token is not None))
                local_listing = generate_movie_listings(args.local_address[0], args.api_token[0])
            else:
                sys.exit("Plex Compare Error: Local Listing File Not Specified")
        else:
            with open(args.compare[1], 'r') as listing_file:
              local_listing = json.load(listing_file)
        plex_compare(remote_listing, local_listing)
    else:
        with open(args.listing[0], 'w') as listing_file:
            json.dump(generate_movie_listings(args.local_address[0], args.api_token[0]), listing_file, indent=4) 
