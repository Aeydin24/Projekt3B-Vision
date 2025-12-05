import numpy as np

# note til mig selv husk a tilføj confidense 0-100%
class productType:
    def __init__(self, name, shape, priority, lower_color, upper_color, min_area, max_area, z_pick):
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

blue_box = productType(
	name="blue_box",
	shape="box",
    priority=2,
	lower_color=[4, 120, 80],
	upper_color=[34, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)

green_box = productType(
	name="green_box",
	shape="box",
    priority=1,
	lower_color=[35, 120, 120],
	upper_color=[65, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)

red_pill_glass = productType(
	name="red_pill_glass",
	shape="circle",
    priority=2,
	lower_color=[158, 120, 120],
	upper_color=[178, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)

green_pill_glass = productType(
	name="green_pill_glass",
	shape="circle",
    priority=1,
	lower_color=[35, 120, 120],
	upper_color=[65, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)

black_pill_glass = productType(
	name="black_pill_glass",
	shape="circle",
    priority=4,
	lower_color=[0, 0, 0],
	upper_color=[0, 0, 50],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)

yellow_pill_glass = productType(
	name="yellow_pill_glass",
	shape="circle",
    priority=1,
	lower_color=[15, 120, 120],
	upper_color=[45, 255, 255],
	min_area=300,
	max_area=50000,
	z_pick=0.10,
)
