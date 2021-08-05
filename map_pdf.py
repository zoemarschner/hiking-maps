from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from PIL import Image
from map_from_gpx_track import *
import os
import reportlab
from reportlab.pdfbase.ttfonts import TTFont


def map_pdf_from_gpx(file_name):
	pdfmetrics.registerFont(TTFont('Futura-Medium', 'Futura-Medium.ttf'))
	pdfmetrics.registerFont(TTFont('Futura-Bold', 'Futura-Bold.ttf'))

	# image dims
	ll = (0.25 * inch, 0.75 * inch)
	dim = {'width': inch * 10.5, 'height': inch * 7.5}


	# get data
	tracks, f_names = map_from_gpx_file(file_name)

	# set up canvas
	c = canvas.Canvas("maps.pdf", pagesize=(inch * 11, inch * 8.5))

	for i, im_fname in enumerate(f_names):
		# draw map
		c.drawImage(im_fname, *ll, **dim)
		
		# draw text
		txt_obj = c.beginText()
		txt_obj.setTextOrigin(0.25 * inch, 0.4 * inch)
		txt_obj.setFont("Futura-Bold", 17)
		txt_obj.textOut("FRENCH RIVER")
		txt_obj.setFont("Futura-Medium", 17)
		txt_obj.textOut(f" DAY {i+1}")
		c.drawText(txt_obj)

		# set path props
		c.setLineJoin(1)
		c.setLineCap(1)
		c.setDash(5, 4)
		#222, 114, 106
		# c.setStrokeColorRGB(222/255, 114/255, 106/255)
		c.setStrokeColorRGB(255/255, 0/255, 0/255)

		# draw path
		path = c.beginPath();

		np_dim = np.array([dim['width'], dim['height']])
		np_ll = np.array(ll)
		
		for i, pt in enumerate(tracks[i]):
			pdf_pt = pt * np_dim + np_ll

			if i == 0:
				path.moveTo(*pdf_pt)
			else:
				path.lineTo(*pdf_pt)

		c.drawPath(path)
		c.showPage()

	c.save()


if __name__ == "__main__":
	if len(sys.argv) <= 1:
		raise Exception('No gpx file provided.')

	file_name = sys.argv[1]
	map_pdf_from_gpx(file_name)