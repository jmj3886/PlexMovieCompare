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
            "directory and compares them for differences between two "
            "Plex servers.",
            conflict_handler="resolve",
        )
        self._arg_parser.add_argument(
            "remote_address",
            nargs=1,
            type=str,
            metavar="<REMOTE_SERVER_ADDRESS>",
            help="The IP address of the remote Plex server.",
        )
        self._arg_parser.add_argument(
            "local_address",
            nargs=1,
            type=str,
            metavar="<LOCAL_SERVER_ADDRESS>",
            help="The IP address of the local Plex server.",
        )
        self._arg_parser.add_argument(
            "api_token",
            nargs=1,
            type=str,
            metavar="<API_TOKEN>",
            help="The API token for connecting to Plex Web API.",
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


def generate_movie_listings(remote_address, local_address, plex_token):
    remote_listing = []
    remote_libraries = get_plex_libraries(remote_address, plex_token)
    get_plex_library_content(remote_address, plex_token, remote_libraries)

    local_listing = []
    local_libraries = get_plex_libraries(local_address, plex_token)
    get_plex_library_content(local_address, plex_token, local_libraries)

    for library in remote_libraries:
        for movie in library["Movies"]:
            remote_listing.append(
                {"Title": movie["Title"], "Library": library["Title"]}
            )
    for library in local_libraries:
        for movie in library["Movies"]:
            local_listing.append({"Title": movie["Title"], "Library": library["Title"]})
    return remote_listing, local_listing


if __name__ == "__main__":
    args = CommandLineParser().parse_info()
    if args.compare is not None:
        with open(args.compare[0], 'r') as listing_file:
          remote_listing = json.load(listing_file)
        with open(args.compare[1], 'r') as listing_file:
          local_listing = json.load(listing_file)
    else:
        remote_listing, local_listing = generate_movie_listings(
            args.remote_address[0], args.local_address[0], args.api_token[0]
        )

    plex_compare(remote_listing, local_listing)
