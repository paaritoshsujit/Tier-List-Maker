# import statements - in-built
import json
import os
from datetime import datetime
from io import BytesIO
from typing import List

# import statements - pylast based
import pylast
import requests
from pick import pick
from PIL import Image, ImageDraw, ImageFont
from rich import print
from rich.panel import Panel
from rich.table import Table

###############################################


# Function ensuring that a file exists to store data in 
def load_or_create_json():
    # check if the file already exists
    if os.path.exists("albums.json"):
        with open("albums.json") as f:
            ratings = json.load(f)
    # create a new json file if it doesnt exist
    else:
        with open("albums.json", "w") as f:
            ratings = {"album_ratubgs": [],"song_ratings":[], "tier_lists": [] }
            json.dump(ratings, f)
        
###############################################

############### UTILITY FUNCTIONS #############


# to remove a picked album from the list to avoid repetitions.
# returns a list of albums picked for the current tier.
def create_tier_list_helper(albums_to_rank, tier_name):
    # if no albums, return empty list
    if not albums_to_rank:
        return []
    
    question = (f"Select the albums you want to rank in {tier_name}")
    # Allow user to pick mulitple albums for current tier
    tier_picks = pick(options=albums_to_rank, title=question, multiselect=True)
    tier_picks = [x[0] for x in tier_picks]

    # Remove each selected from the original list
    for album in tier_picks:
        albums_to_rank.remove(album)

    return tier_picks


# Returns the cover of an album that a user has selected
def get_album_cover(artist, album):
    album = network.get_album(artist, album)
    album_cover = album.get_cover_image()

    # check if the URL is valid
    try:
        response = requests.get(album_cover)
        # Request 200 is the OK response
        if response.status_code != 200:
            album_cover = "https://community.mp3tag.de/uploads/default/original/2X/a/acf3edeb055e7b77114f9e393d1edeeda37e50c9.png"
    except:
        album_cover = "https://community.mp3tag.de/uploads/default/original/2X/a/acf3edeb055e7b77114f9e393d1edeeda37e50c9.png"

    return album_cover


# returns a list of all the albums created by the artist
def get_album_list(artist: str) -> List[str]:
    # GET THE TOP ALBUMS OF THE ARTIST AND STORE THEM IN A LIST
    artist = network.get_artist(artist)
    top_albums = artist.get_top_albums()
    album_list = [str(album.item) for album in top_albums]

    # CLEANUP THE LIST
    for album in album_list:
        if "(null)" in album:
            album_list.remove(album)

    # SORT THE LIST
    album_list.sort()

    # ADD EXIT OPTION
    album_list.insert(0, "EXIT")
    return album_list


###############################################

################ MENU FUNCTIONS ###############

def create_tier_list():
    load_or_create_json()
    with open("albums.json") as f:
        album_file = json.load(f)

    print("TIERS -  S, A, B, C, D, E")

    question = "Which artist do you want to make a tier list for?"
    artist = input(question).strip().lower()

    try:
        get_artist = network.get_artist(artist)
        artist = get_artist.get_name()
        albums_to_rank = get_album_list(artist)

        # keep only the album name splitting and removing the characters before the first '-'
        albums_to_rank = [x.split('-', 1)[1] for x in albums_to_rank[1:]]

        question = "What do you want to call the tier list?"
        tier_list_name =  input(question).strip()

        # S Tier Albums
        s_tiers = create_tier_list_helper(albums_to_rank, "S Tier")
        s_covers = [get_album_cover(artist, album) for album in s_tiers]
        s_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(s_tiers, s_covers)]

        # A Tier Albums
        a_tiers = create_tier_list_helper(albums_to_rank, "A Tier")
        a_covers = [get_album_cover(artist, album) for album in a_tiers]
        a_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(a_tiers, a_covers)]

        # B Tier Albums
        b_tiers = create_tier_list_helper(albums_to_rank, "B Tier")
        b_covers = [get_album_cover(artist, album) for album in b_tiers]
        b_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(b_tiers, b_covers)]

        # C Tier Albums
        c_tiers = create_tier_list_helper(albums_to_rank, "C Tier")
        c_covers = [get_album_cover(artist, album) for album in c_tiers]
        c_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(c_tiers, c_covers)]

        # D Tier Albums
        d_tiers = create_tier_list_helper(albums_to_rank, "D Tier")
        d_covers = [get_album_cover(artist, album) for album in d_tiers]
        d_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(d_tiers, d_covers)]

        # E Tier Albums
        e_tiers = create_tier_list_helper(albums_to_rank, "E Tier")
        e_covers = [get_album_cover(artist, album) for album in e_tiers]
        e_tier_final = [{'album': album, 'cover_art': cover} for album, cover in zip(e_tiers, e_covers)]
    

        # Check if all tiers are empty, if so then exit
        if not any([s_tier_final, a_tier_final, b_tier_final, c_tier_final, d_tier_final, e_tier_final]):
            print("All tiers are empty. Exiting...")
            return
        
        # Add the albums that were picked to the tier list
        tier_list = {
            'tier_list_name' : tier_list_name,
            'artist' : artist,
            's_tier' : s_tier_final,
            'a_tier' : a_tier_final,
            'b_tier' : b_tier_final,
            'c_tier' : c_tier_final,
            'd_tier' : d_tier_final,
            'e_tier' : e_tier_final,
            'time' : str(datetime.now())
        }

        # Add the tier list to the JSON file
        album_file['tier_lists'].append(tier_list)

        # Save the JSON file
        with open('albums.json', 'w') as f:
            json.dump(album_file, f, indent=4)

        return

    except pylast.PyLastError:
        print("❌[b red] Artist not found [/b red]")

###############################################
############# TIER LIST VISUALIZER ############

def image_generator(file_name, data):
    # return if the file already exists
    if os.path.exists(file_name):
        return
    
    # Set total image size and font
    img_width = 1920
    img_height = 5000
    font = ImageFont.truetype("arial.ttf", 15)
    tier_font = ImageFont.truetype("arial.ttf", 30)

    # Create the image i.e. black background
    image = Image.new("RGB", (img_width, img_height), "black")
    text_cutoff_value = 20

    # Initialize variables for row and column positions
    row_pos = 0
    col_pos = 0
    increment_size = 200


    '''S Tier'''
    # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="red")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "S Tier", font=tier_font, fill="white")
        col_pos += increment_size

    for album in data['s_tier']:
        # gettin the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))

        # Resize cover art
        cover_art = cover_art.resize((increment_size, increment_size))

        # Past the cover art onto the base image
        image.paste(cover_art,(col_pos, row_pos))

        # Draw the album name on the image in white, font 10
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the col position
        col_pos += increment_size
        # check if the col position > image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0

    # Add a new row to seperate from the next tier
    row_pos += increment_size+50
    col_pos = 0


    '''A Tier'''
    # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="orange")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "A Tier", font=tier_font, fill="white")
        col_pos += increment_size

    for album in data['a_tier']:
        # gettin the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))

        # Resize cover art
        cover_art = cover_art.resize((increment_size, increment_size))

        # Past the cover art onto the base image
        image.paste(cover_art,(col_pos, row_pos))

        # Draw the album name on the image in white, font 10
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the col position
        col_pos += increment_size
        # check if the col position > image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0

    # Add a new row to seperate from the next tier
    row_pos += increment_size+50
    col_pos = 0


    """B TIER"""
    # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="yellow")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "B Tier", font=tier_font, fill="black")
        col_pos += increment_size
        
    for album in data["b_tier"]:
        # Get the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))
        # Resize the cover art
        cover_art = cover_art.resize((increment_size, increment_size))
        # Paste the cover art onto the base image
        image.paste(cover_art, (col_pos, row_pos))
        # Draw the album name on the image with the font size 10 and background color white
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the column position
        col_pos += 200
        # check if the column position is greater than the image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0
    
    # add a new row to separate the tiers
    row_pos += increment_size + 50
    col_pos = 0
    
    """C TIER"""
        # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="green")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "C Tier", font=tier_font, fill="black")
        col_pos += increment_size
        
    for album in data["c_tier"]:
        # Get the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))
        # Resize the cover art
        cover_art = cover_art.resize((increment_size, increment_size))
        # Paste the cover art onto the base image
        image.paste(cover_art, (col_pos, row_pos))
        # Draw the album name on the image with the font size 10 and background color white
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the column position
        col_pos += 200
        # check if the column position is greater than the image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0
    
    # add a new row to separate the tiers
    row_pos += increment_size + 50
    col_pos = 0
   

    """D TIER"""
    # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="blue")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "D Tier", font=tier_font, fill="black")
        col_pos += increment_size
        
    for album in data["d_tier"]:
        # Get the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))
        # Resize the cover art
        cover_art = cover_art.resize((increment_size, increment_size))
        # Paste the cover art onto the base image
        image.paste(cover_art, (col_pos, row_pos))
        # Draw the album name on the image with the font size 10 and background color white
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the column position
        col_pos += 200
        # check if the column position is greater than the image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0
    
    # add a new row to separate the tiers
    row_pos += increment_size + 50
    col_pos = 0


    """E TIER"""
        # leftmost side - make a square with text inside the square and fill color
    if col_pos == 0:
        draw = ImageDraw.Draw(image)
        draw.rectangle((col_pos, row_pos, col_pos + increment_size, row_pos + increment_size), fill="pink")
        draw.text((col_pos + (increment_size//3), row_pos+(increment_size//3)), "E Tier", font=tier_font, fill="black")
        col_pos += increment_size
        
    for album in data["e_tier"]:
        # Get the cover art
        response = requests.get(album["cover_art"])
        cover_art = Image.open(BytesIO(response.content))
        # Resize the cover art
        cover_art = cover_art.resize((increment_size, increment_size))
        # Paste the cover art onto the base image
        image.paste(cover_art, (col_pos, row_pos))
        # Draw the album name on the image with the font size 10 and background color white
        draw = ImageDraw.Draw(image)

        # Get the album name
        name = album["album"]
        if len(name) > text_cutoff_value:
            name = f"{name[:text_cutoff_value]}..."

        draw.text((col_pos, row_pos + increment_size), name, font=font, fill="white")

        # Increment the column position
        col_pos += 200
        # check if the column position is greater than the image width
        if col_pos > img_width - increment_size:
            # add a new row
            row_pos += increment_size + 50
            col_pos = 0
    
    # add a new row to separate the tiers
    row_pos += increment_size + 50
    col_pos = 0


    # crop the image to trim the extra space below the last row
    image = image.crop((0,0, img_width, row_pos))

    # save the image 
    image.save(f"{file_name}")



# To render the image of a tier list
def see_tier_lists():
    load_or_create_json()
    with open("albums.json", "r") as f:
        data = json.load(f)

    if not data['tier_lists']:
        print("❌ [b red]No tier lists have been created yet![/b red]")
        return
    
    for key in data['tier_lists']:
        image_generator(f"{key['tier_list_name']}.png", key)
        print(f"✅ [b green]CREATED[/b green] {key['tier_list_name']} tier list.")

    print("✅ [b green]DONE[/b green]. Check the directory for the tier lists.")    
    return

###############################################

# retrieving the API_KEY from the env variables of the system
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET= os.environ.get("LASTFM_API_SECRET")
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

############### DRIVER FUNCTION ###############
def start():
    global network
    startup_question= "What do you want to do?"
    options = ["Rate by album", "Rate Songs", "See Albums Rated", "See Songs Rated", "Make a tier list", "See Created Tier Lists", "EXIT"]
    selected_option, index = pick(options=options, title=startup_question, indicator="→")

    if index == 0:
        rate_by_album()
    elif index == 1:
        rate_by_song()
    elif index == 2:
        see_albums_rated()
    elif index == 3:
        see_songs_rated()
    elif index == 4:
        create_tier_list()
    elif index == 5:
        see_tier_lists()
    elif index == 6:
        exit()

start()