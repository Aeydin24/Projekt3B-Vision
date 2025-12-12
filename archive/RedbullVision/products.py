import numpy as np
redDepot = [-0.26125, -0.20881, 0.04]  
greenDepot = [-0.3500, -0.34612, 0.04]  
yellowDepot = [-0.328768, -0.2242, 0.04]  
restDepot = [-0.3, -0.066, 0.04] # depot for alt andet, Vi skal lige give den en position :)

class productType:
	def __init__(self, name, shape, priority, lower_color, upper_color, min_area, max_area, z_pick, depot_location):
		self.name = name
		self.shape = shape
		self.priority = priority # lavere nummer = højere prioritet
		# HSV-farver som numpy-arrays
		self.lower_color = np.array(lower_color, dtype=np.uint8)
		self.upper_color = np.array(upper_color, dtype=np.uint8)
		self.min_area = min_area
		self.max_area = max_area
		# z-højde hvor vi vil samle objektet op (i meter)
		self.z_pick = z_pick
		self.depot_location = depot_location  # (x, y, z) koordinater for depot

blue_box = productType(
	name="blue_box",
	shape="box",
    priority=2,
	lower_color=[4, 120, 80],
	upper_color=[34, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=restDepot
)

green_box = productType(
	name="green_box",
	shape="box",
    priority=1,
	lower_color=[35, 120, 120],
	upper_color=[65, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=greenDepot
)

red_pill_glass = productType(
	name="red_pill_glass",
	shape="circle",
    priority=2,
	lower_color=[0, 148, 136],
	upper_color=[10, 255, 255],
	min_area=300,
	max_area=4000,
	z_pick=0.02,
    depot_location=redDepot
)

green_pill_glass = productType(
	name="green_pill_glass",
	shape="circle",
    priority=1,
	lower_color=[38, 109, 109],
	upper_color=[58, 229, 229],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=greenDepot
)

blue_pill_glass = productType(
	name="blue_pill_glass",
	shape="circle",
    priority=1,
	lower_color=[91, 153, 110],
	upper_color=[111, 255, 230],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=yellowDepot
)


black_pill_glass = productType(
	name="black_pill_glass",
	shape="circle",
    priority=4,
	lower_color=[0, 0, 0],
	upper_color=[0, 0, 50],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=restDepot
)

yellow_pill_glass = productType(
	name="yellow_pill_glass",
	shape="circle",
    priority=1,
	lower_color=[15, 120, 120],
	upper_color=[45, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
    depot_location=yellowDepot
)

pink_pill_glass = productType(
	name="pink_pill_glass",
	shape="circle",
	priority=4,
	lower_color=[145, 120, 120],
	upper_color=[165, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.02,
	depot_location= redDepot
)