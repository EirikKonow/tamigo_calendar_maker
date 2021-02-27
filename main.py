#TODO
# Remove unused code
# Move help functions
# Add documentation
# Comment code
# Use glob to look for textfile, specify if several
# Add feedback lines

import plan_maker

textfile = "inndata.txt"

def main():
	myPlan = plan_maker.Plan_maker(textfile, rows=6)

	myPlan.extract_text()

	myPlan.export_plan()


if __name__ == '__main__':
	main()