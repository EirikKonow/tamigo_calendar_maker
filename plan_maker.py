from PIL import Image, ImageDraw, ImageFont
import glob
import datetime
# 72


class Plan_maker:
	"""
	ADD DOCUMENTATION!
	"""
	def __init__(self, textFile, rows=6, columns=7,
				size=(297,210), border= 2, scale = 5):
		self.textFile = textFile
		self.rows = rows
		self.columns = columns
		self.day_size = (int(size[0]/columns)*scale+border,int(size[1]/rows)*scale+border)
		self.size = (self.day_size[0]*columns, self.day_size[1]*rows)
		self.border = border
		self.scale = scale
		self.plan_list = []


	def make_dict(self) -> dict:
		"""
		Constructs and returns an empty
		version of the dictionaries used by this class.
		"""

		plan_dict = {"week":None,
					"weekday"	:["man.","tir.","ons.","tor.","fre.","lør.","søn.",],
					"date"		:[None for i in range(7)],
					"start_time":[None for i in range(7)],
					"end_time"	:[None for i in range(7)],
					"hours"		:[None for i in range(7)],
					"year"		:[None for i in range(7)]
					}
		return plan_dict


	def can_be_int(self, value: str) -> bool:
		"""
		Help function for checking if a value can be converterd to int.
		"""

		try:
			int(value)
			return True
		except ValueError:
			return False


	def time2part_of_day(self, time_str: str) -> int:
		"""
		Takes in a military time value as a string and
		converts it into a decimal value for positioning on a "day-line"
		! Client has requested the day starts at 8am and ends at 11:30pm.
		"""

		if not time_str:
			return 0
		# Converting the time into decimal value and offsets by 8 hours.
		hours = int(time_str.split(':')[0])*100 - 800
		minutes = int(time_str.split(':')[1])/60.0*100
		time = hours+minutes
		# Maps the time value onto the size of the image.
		ratio = (self.day_size[1]-self.border)/(2400.0-50-800)
		time = ratio*time
		return int(time)


	def fix_dates(self):
		"""
		A help function for filling in 
		missing dates after extraing the text form file.
		"""

		days_since_monday = 0
		anchor_date = datetime.datetime(2000,1,1)
		# Copies list to not change it while iterating through it
		copy_list = self.plan_list
		# Loops through every weeks dicitonary
		for i, dic in enumerate(self.plan_list):
			# Loops in a dicitonarys dates until it find a valid date to use as reference
			for date in dic["date"]:
				if not date:
					days_since_monday += 1
				if date:
					date_data = date.split(".")
					date_data = [int(d) for d in date_data]
					anchor_date = datetime.datetime(date_data[2],date_data[1],date_data[0])
					break

			# Replaces all dates to fill in empty ones
			startdate = anchor_date - datetime.timedelta(days_since_monday)
			for j in range(7):
				newdate = startdate + datetime.timedelta(j)
				copy_list[i]["date"][j] = "{}.{}.{}".format(newdate.day, newdate.month, newdate.year)
			days_since_monday = 0

		self.plan_list = copy_list


	def extract_text(self):
		week_dict = self.make_dict()
		with open(self.textFile, 'r+', encoding='utf-8-sig') as file:
			for line in file:
				words = line.split()
				if words:
					if self.can_be_int(words[0]) and len(words) >= 6:
						# For initial week
						if week_dict["week"] == None: # if not week_dict["weekday"]   maybe
							week_dict["week"] = words[0]
						if week_dict["week"] == words[0]:
							for i, weekday in enumerate(week_dict["weekday"], start=0):
								if weekday == words[1]:
									week_dict["date"][i] = words[2]
									week_dict["start_time"][i] = words[3].split('-')[0]
									week_dict["end_time"][i] = words[3].split('-')[1]
									week_dict["hours"][i] = words[4]
									week_dict["year"][i] = words[5]
						
						else:
							self.plan_list.append(week_dict)
							week_dict = self.make_dict()
							week_dict["week"] = words[0]
							for i, weekday in enumerate(week_dict["weekday"], start=0):
								if weekday == words[1]:
									week_dict["date"][i] = words[2]
									week_dict["start_time"][i] = words[3].split('-')[0]
									week_dict["end_time"][i] = words[3].split('-')[1]
									week_dict["hours"][i] = words[4]
									week_dict["year"][i] = words[5]

		self.plan_list.append(week_dict)	

		self.fix_dates()
						


	def make_day_img(self, start_time="9:00", end_time="22:00", date="???", weekday="man", week="??"):
		fnt = ImageFont.truetype("arial.ttf", 14)
		start_time_txt = start_time

		# Background, black
		day_img = Image.new('RGB', self.day_size, (120,120,120))
		# "Visible" area, makes the background into a rim
		day_img_inner = Image.new('RGB', (self.day_size[0]-self.border, self.day_size[1]-self.border), (250,250,250))
		
		
		# Rectangle based on start-end time
		if start_time_txt:
			start_time = self.time2part_of_day(start_time)# - 800
			end_time = self.time2part_of_day(end_time)
			work_part = Image.new('RGBA', (day_img_inner.size[0], (end_time-start_time)), (180,180,180,128))
			draw_clock = ImageDraw.Draw(work_part)
			w_txt, h_txt = draw_clock.textsize(start_time_txt)
			draw_clock.text(((work_part.size[0]-w_txt)/2,10), start_time_txt, font=fnt, fill=(100,100,100,196))
			# Adds work_hours to "visible" area.
			day_img_inner.paste(work_part, (0,start_time))

		#Adds date as text to monday
		draw_text = ImageDraw.Draw(day_img_inner)
		
		if weekday == "søn.":
			draw_text.text((self.day_size[0] - 30,10), date.split(".")[0], font=fnt, fill=(100,100,100,126))
		if weekday == "man.":
			draw_text.text((10,self.day_size[1]-10-14), week, font=fnt, fill=(100,100,100,126))
		
		# Paste "visible" area inside border
		day_img.paste(day_img_inner, (int(self.border/2), int(self.border/2)))

		return day_img


	def make_week_img(self, n: int):
		week_img = Image.new('RGB', (self.day_size[0]*7, self.day_size[1]), (250,250,250))
		for i, day in enumerate(self.plan_list[n]["weekday"]):
			day_img = self.make_day_img(start_time=self.plan_list[n]["start_time"][i],
										end_time=self.plan_list[n]["end_time"][i],
										date=self.plan_list[n]["date"][i],
										weekday=day,
										week=self.plan_list[n]["week"],
										)
			week_img.paste(day_img, (self.day_size[0]*i, 0))
			#week_img.save("week_{}.jpg".format(n), "JPEG")


		return week_img


	def export_plan(self):
		week_imgs = []
		plan_img = Image.new('RGB', (self.size[0], self.size[1]), (250,250,250))
		for n, week in enumerate(self.plan_list):
			week_imgs.append(self.make_week_img(n))

		for i, week_img in enumerate(week_imgs):
			plan_img.paste(week_imgs[i], (0, self.day_size[1]*i))


		plan_img.save("printable.jpg", "JPEG")


