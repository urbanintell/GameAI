'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, random, time, copy
import numpy as np
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a grid as a 2D array of True/False values (True =  traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
	dimensions = (0, 0)

	dim = world.getDimensions()
	grid = np.array([[True]*dim[1]]*dim[0])
	dimensions = (dim[0],dim[1])
	obstacles = world.getObstacles()
	point_list = []
	line_list = []
	
	for obstacle in obstacles:
		point_list.append(obstacle.getPoints())

	for points in point_list:
		for i in range(0,len(points)):
			for j in range(i+1,len(points)):
				line_list.append((points[i],points[j]))

	for i in range(dim[0]):
		for j in range(dim[1]):
			for polygon in point_list:
				if pointInsidePolygonPoints((i*cellsize,j*cellsize),polygon):
					grid[i][j] = False

					if (i-1)*cellsize >= 0:
						grid[i-1][j] = False
					if (j-1)*cellsize >= 0:
						grid[i][j-1] = False
					if (i-1)*cellsize >= 0 and (j-1)*cellsize >= 0:
						grid[i-1][j-1] = False

				if pointOnPolygon((i*cellsize,j*cellsize),polygon):
					grid[i][j] = False

				x1 = i*cellsize
				y1 = j*cellsize
				x2 = (i+1)*cellsize
				y2 = (j+1)*cellsize

				grid_polygon = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]

				for point in polygon:
					if pointInsidePolygonPoints(point,grid_polygon):
						grid[i][j] = False
					if pointOnPolygon(point,grid_polygon):
						grid[i][j] = False


	return grid, dimensions

