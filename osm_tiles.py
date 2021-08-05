from PIL import Image
import math
import numpy as np
from tqdm import tqdm
import requests
from os.path import isfile, join


URLS = {'mapbox': ("https://api.mapbox.com/styles/v1/zoemarschner/ckqmk3o3v0q8y17mx3y0v8hu2/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoiem9lbWFyc2NobmVyIiwiYSI6ImNrYW16eXdibTB1eDgyenBrZXJkb2txZzUifQ.Xbmkj-0Dqf-e1zn_RWuh-Q", 512),
		'watercolor': ("https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg", 256),
		'toner': ("https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png", 256),
		'outdoors': ("https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=899e5b713c984073b51950fc2c198908", 256)}

# tile res is the minimum number of tiles in the height/width, used when making maps
TILE_RES = 4

map_cache_path = '/Users/zoe/proj/2021/hiking_map/map_cache'

"""
loads tile for given x, y 
zoom levels between 0-22
coordinates are the standard "slippy tile" coordinates
"""
def load_tile(z, x, y, style_format):
	try:
		rq = requests.get(style_format.format(z=z, x=x, y=y), stream=True)
		im = Image.open(rq.raw)	
		# print(URL_TEMPLATE.format(z=z, x=x, y=y))
		return im
	except:
		print(f'Error at {style_format.format(z=z, x=x, y=y)}')


"""
converts lat/lon to the xy of the tile, scaled between 0-1
"""
def latlon_to_xy(coord):
	coord = np.array(coord)
	coord = (coord * math.pi)/180

	lat, lon = coord.T

	x = -lon
	y = np.log(np.tan(lat) + 1/np.cos(lat))

	X = np.array([x.T, y.T]).T
	X = (1 - X/math.pi)/2

	return X

"""
converts xy of tile, between 0-1, to a given zoom level.
"""
def zoom_xy(X, zoom):
	N = 2 ** zoom
	tX = (X * N)
	return tX

# recalculates bounds to add padding and fix aspect ratio
def fix_ar(tlX, brX, ar, pad):
	# add padding
	cur_dims = brX - tlX

	# x(1 - pad) = w * pad
	padding = cur_dims * (pad/(1-pad))
	pad_dims = cur_dims + padding
	w, h = pad_dims;

	# fir aspect ratio
	cur_AR = w/h

	if cur_AR > ar:
		x = (w - ar * h)/ar
		padding[1] += x
	else:
		x = h * ar - w
		padding[0] += x


	brX = brX + padding/2
	tlX = tlX - padding/2

	return tlX, brX


def load_map(tl, br, ar, pad, name):
	tlX = latlon_to_xy(tl)
	brX = latlon_to_xy(br)
	tlX, brX = fix_ar(tlX, brX, ar, pad)
	Xdiff = brX - tlX;
	min_diff = np.min(Xdiff)
	zoom = int(np.ceil(np.log2(TILE_RES/min_diff)))


	tl_tX_raw = zoom_xy(tlX, zoom)
	br_tX_raw = zoom_xy(brX, zoom)

	tl_tX = tl_tX_raw.astype(int)
	br_tX = br_tX_raw.astype(int)
	
	format_str, size = URLS['mapbox']

	avg_lat = tl
	res = resolution = 156543.03 meters/pixel * cos(latitude) / (2 ^ zoom) * (256/size)

	im_size = np.array([size, size])
	total_size = (br_tX - tl_tX + 1) * im_size


	track_fname = join(map_cache_path, f'{name}.png')
	if not isfile(track_fname):
		tiled_im = Image.new('RGBA', tuple(total_size))
		with tqdm(total=np.prod(br_tX - tl_tX + 1)) as pbar:
			for i in range(tl_tX[0], br_tX[0] + 1):
				for j in range(tl_tX[1], br_tX[1] + 1):
					im = load_tile(zoom, i, j, format_str)
					im_coords = (np.array([i, j]) - tl_tX)*im_size

					tiled_im.paste(im, tuple(im_coords))
					pbar.update(1)

		org_size = br_tX - tl_tX + 1
		top = (tl_tX_raw - tl_tX)/org_size * total_size
		bot = (br_tX_raw - tl_tX)/org_size * total_size

		tiled_im = tiled_im.crop((top[0], top[1], bot[0], bot[1]))

		tiled_im.save(track_fname)

	return zoom, tlX, brX, track_fname
		


if __name__ == "__main__":

	# # Leslieville test
	# tl = [43.668727, -79.355091]
	# br = [43.656597, -79.305111]

	# Kawartha lakes
	tl = [44.637507, -78.119857]
	br = [44.596706, -78.027178]

	# tl = [44.630275, -78.065416]
	# br = [44.623121, -78.045027]
# 47.372260, 8.552522
	load_map(tl, br)


