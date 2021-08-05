from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from PIL import Image
from map_from_gpx_track import *
import os
import reportlab
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth


def map_pdf_from_gpx(file_name):
	pdfmetrics.registerFont(TTFont('Futura-Medium', 'Futura-Medium.ttf'))
	pdfmetrics.registerFont(TTFont('Futura-Bold', 'Futura-Bold.ttf'))

	# image dims
	ll = (0.25 * inch, 0.75 * inch)
	dim = {'width': inch * 10.5, 'height': inch * 7.5}

	tp = (0.25 * inch, 0.4 * inch)

	# get data
	tracks, f_names, scales = map_from_gpx_file(file_name)

	# set up canvas
	c = canvas.Canvas("maps.pdf", pagesize=(inch * 11, inch * 8.5))

	for i, im_fname in enumerate(f_names):
		# draw map
		c.drawImage(im_fname, *ll, **dim)
		
		# draw text
		txt_obj = c.beginText()
		txt_obj.setCharSpace(0.5)
		txt_obj.setTextOrigin(*tp)
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

		for j, pt in enumerate(tracks[i]):
			pdf_pt = pt * np_dim + np_ll

			if j == 0:
				path.moveTo(*pdf_pt)
			else:
				path.lineTo(*pdf_pt)

		c.drawPath(path)

		# draw scale
		c.setDash([])
		c.setStrokeColorRGB(0,0,0)
		c.setLineWidth(0.5)

		scale_hgt = 0.05 * inch
		scale = scales[i] * dim['width']
		scale_path = c.beginPath()
		scale_path.moveTo(ll[0] + dim['width'], tp[1] + scale_hgt)
		scale_path.lineTo(ll[0] + dim['width'], tp[1])
		scale_path.lineTo(ll[0] + dim['width'] - scale, tp[1])
		scale_path.lineTo(ll[0] + dim['width'] - scale, tp[1] + scale_hgt)
		c.drawPath(scale_path)

		scale_str = "1 km"
		str_width = stringWidth(scale_str, "Futura-Medium", scale_hgt*2)
		scale_txt = c.beginText()
		scale_txt.setCharSpace(0)
		scale_txt.setTextOrigin(ll[0] + dim['width'] - scale - str_width - scale_hgt, tp[1])
		scale_txt.setFont("Futura-Medium", scale_hgt*2)
		scale_txt.textOut(scale_str)
		c.drawText(scale_txt)


		c.showPage()

	c.save()


if __name__ == "__main__":
	if len(sys.argv) <= 1:
		raise Exception('No gpx file provided.')

	file_name = sys.argv[1]
	map_pdf_from_gpx(file_name)