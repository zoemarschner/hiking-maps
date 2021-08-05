import gpxpy
import sys
import numpy as np
import matplotlib.pyplot as plt
from osm_tiles import *
	

def map_from_gpx_file(file_name):
	gpx_file = open(file_name, 'r')
	gpx = gpxpy.parse(gpx_file)

	tracks = []
	f_names = []
	scales = []

	for i, track in enumerate(gpx.tracks):
		track_points = []

		for segment in track.segments:
			for point in segment.points:
				track_points.append([point.latitude, point.longitude])
		
		track_points = np.array(track_points)
		pts, name, scale_amt = map_for_track(track_points, 10.5/7.5, .1, track.name)
		tracks.append(pts)
		f_names.append(name)
		scales.append(scale_amt)

	return tracks, f_names, scales

# makes map for gpx track, returns scaled track_points
def map_for_track(gpx_trackpoints, ar, pad, name):
	# calculate bounds of gpx track
	max_pt = np.max(gpx_trackpoints, axis=0)
	min_pt = np.min(gpx_trackpoints, axis=0)

	tl = (max_pt[0], min_pt[1])
	br = (min_pt[0], max_pt[1])

	zoom, tlX, brX, fname, scale_amt = load_map(tl, br, ar, pad, name)

	scale_pts = latlon_to_xy(gpx_trackpoints)
	scale_pts = (scale_pts - tlX) / (brX - tlX)
	scale_pts[:, 1] = 1- scale_pts[:, 1]

	return scale_pts, fname, scale_amt



if __name__ == "__main__":
	if len(sys.argv) <= 1:
		raise Exception('No gpx file provided.')

	file_name = sys.argv[1]
	map_from_gpx_file(file_name)