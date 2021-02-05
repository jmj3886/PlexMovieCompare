# PlexMovieCompare
Generates Movie Listings from a Plex directory and compares them for differences between two Plex servers.

## Running PlexMovieCompare

### Getting Plex API Token
    1. Open https://app.plex.tv/desktop
    2. Right-Click inside window
    3. Select Inpsect
    4. In the Inpsect window, Select the "Application" tab
    5. In the left menu Select "Local Storage", then "https://app.plex.tv
    6. The Plex API Token will be listed under "myPlexAccessToken"
    7. Copy the value String for use later

### Creating Listing From Local Server
The Plex API cannot be used for remote servers. Plex uses backend logic to traverse to remote servers, therefore listings must be created on the local network.

#### Creating Listing

    Required Information:
        - IP Address of Plex Server on Local Network
        - Plex API Token

    1. Execute the following command:
        - python PlexMovieCompare.py --listing_file <LISTING_FILENAME> --local_address <PLEX_SERVER_IP_ADDRESS> --api_token <PLEX_API_TOKEN>
    2. Listing file will be created at the filepath specified by <LISTING_FILENAME>

### Comparing Listings
    
#### Comparing Two Files

    Required Information:
        - Remote Plex Listing File
        - Local Plex Listing File

    1. Execute the following command:
        - python PlexMovieCompare.py --compare RemoteListing.json LocalListing.json
    2. Difference file will be created in the directory in which PlexMovieCompare is run
    
#### Comparing File and Local Plex Server

    Required Information:
        - Remote Plex Listing File
        - IP Address of Plex Server on Local Network
        - Plex API Token

    1. Execute the following command:
        - python PlexMovieCompare.py  --local_address <PLEX_SERVER_IP_ADDRESS> --api_token <PLEX_API_TOKEN> --compare RemoteListing.json
    2. Difference file will be created in the directory in which PlexMovieCompare is run
    
