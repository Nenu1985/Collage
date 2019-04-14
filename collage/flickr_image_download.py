'''
Module download images from flickr.com in parallel mode
You should install flickrapi:
pip install flickrapi
'''
#
import os
import urllib
from multiprocessing import Pool
from itertools import repeat
import flickrapi
from PIL import Image

from . import resize_images


FLICKR_PUBLIC = '1f9874c1a8ea5a85acfd419dd0c2c7e1'
FLICKR_SECRET = '67de04d2825fd397'



def create_photo_path(path):
    """
    Create folder 'path' in current work dir
    :param path: folde name
    :return: none
    """
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Directory creation %s failed" % path)
        else:
            print("Directory successfully created:   %s " % path)

# Download the file from `url` and save it locally under `file_name`:
# Executing in parallel mode
def process_url(url, num, i_w):
    """
    Download the file from `url` and save it locally under `file_name`:
    Executing in parallel mode
    :param url: img url
    :param num: img count
    :param i_w: im width
    :return: none: imgs are stored on disc
    """
    if url:    # if url is is - download an image
        urllib.request.urlretrieve(url, 'photo\\i0000' + str(num) + '.jpg')
    else:               # else - save an empty image
        Image.new('RGB', (i_w - 1, i_w-1), (255, 255, 255)).save('photo\\i0000' + str(num) + '.jpg')


def get_urls_from_flickr_generator(photos, num_i: int, url_s: str):
    """
    Tage photo urls
    :param photos: photo generator
    :param num_i: num photo
    :param url_s: extras string
    :return:
    """
    urls = []
    num_of_photos = num_i-2

    for i, photo in enumerate(photos):
        url = photo.get(url_s)

        if url: #if url is empty - pass it and increment photo number
            urls.append(url)
        else: num_of_photos += 1

        if i > num_of_photos:
            break
    return urls

def main(num_i: int, i_w: int, collage_cols: int):
    """  Connet to flickr.com
    Search photos by tag and size
    Download photos in parallel mode
    Save in the current dir by path: photo\\i0000x.jpg, where x - photo id (1,2 .. etc)
    """

    # Flickr api access key
    flickr = flickrapi.FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, cache=True)
    # tag for searching photos
    keyword = 'girl'

    # Choose the downloaded photos size
    #url_c: URL of medium 800, 800 on longest size image
    #url_m: URL of small, medium size image
    #url_n: URL of small, 320 on longest side size image
    #url_o: URL of original size image
    #url_q: URL of large square 150x150 size image
    #url_s: URL of small suqare 75x75 size image
    #url_sq: URL of square size image
    #url_t: URL of thumbnail, 100 on longest side size image

    url_s = ""
    if i_w > 800:
        url_s = 'url_o'
    elif i_w > 320:
        url_s = 'url_c'
    elif i_w > 150:
        url_s = 'url_m'
    else:
        url_s = 'url_n'


    # get generator photos from flickr
    # see https://www.flickr.com/services/api/flickr.photos.search.html
    '''
    text: A free text search. Photos who's title, description or tags contain the text will be returned. You can exclude results that match a term by prepending it with a - character.
    tag_mode: Either 'any' for an OR combination of tags, or 'all' for an AND combination. Defaults to 'any' if not specified.
    tags: A comma-delimited list of tags. Photos with one or more of the tags listed will be returned. You can exclude results that match a term by prepending it with a - character.
    extras: A comma-delimited list of extra information to fetch for each returned record. Currently supported fields are: description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, geo, tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o
    per_page: Number of photos to return per page. If this argument is omitted, it defaults to 100. The maximum allowed value is 500.
    sort: The order in which to sort returned photos. Deafults to date-posted-desc (unless you are doing a radial geo query, in which case the default sorting is by ascending distance from the point specified). The possible values are: date-posted-asc, date-posted-desc, date-taken-asc, date-taken-desc, interestingness-desc, interestingness-asc, and relevance.
    
    extras details:   http://librdf.org/flickcurl/api/flickcurl-searching-search-extras.html
    
    date_taken      Date item was taken
    date_upload     Date item was uploaded
    geo             Geotagging latitude, longitude and accuracy
    icon_server     Item owner icon fields
    last_update     Date item was last updated
    license         Item License
    machine_tags    Machine tags
    media           Item Format: photo or video
    o_dims          Original item dimensions
    original_format Original item secret and format
    owner_name      Item owner ID
    path_alias      Path alias for owner like /photos/USERNAME
    tags            Item clean tags (safe for HTML, URLs)
    url_c           URL of medium 800, 800 on longest size image
    url_m           URL of small, medium size image
    url_n           URL of small, 320 on longest side size image
    url_o           URL of original size image
    url_q           URL of large square 150x150 size image
    url_s           URL of small suqare 75x75 size image
    url_sq          URL of square size image
    url_t           URL of thumbnail, 100 on longest side size image 
    views           Number of times item has been viewed                                                                                    
    '''
    photos = flickr.walk(text=keyword,
                         tags=keyword,
                         extras=url_s,
                         per_page=100,           # may be you can try different numbers..
                         sort='relevance')

    # get urls
    urls = get_urls_from_flickr_generator(photos, num_i, url_s)

    # create photo dir if not exists
    create_photo_path(os.getcwd() + "\\photo")

    print("\nStart downloading photos in parallel mode with 'pool.starmap()' method. "
          "\n# CPUs = " + str(os.cpu_count()))

    # parallel download photos
    with Pool(processes=os.cpu_count()) as pool:
        pool.starmap(process_url, zip(urls, range(num_i), repeat(i_w)))

    print("\nDownload complete!")

    # go to image processing
    resize_images.main(num_i, i_w, collage_cols)


# enter point
if __name__ == "__main__":
    main(10, 128, 5)
