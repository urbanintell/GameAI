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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

def getEdges(arr, i):

	if i == 0:
		return [arr[1],arr[-1]]
	elif i == len(arr)-1:
		return [arr[0],arr[-2]]
	else:
		return [arr[i-1],arr[i+1]]


# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	
	obstacles = world.getObstacles()
	obstacle_points = []
	point_list = []
	line_list = []
	point_dict = {}
	maxRadius = agent.getMaxRadius()
	
	# build up point list and line list from obstacles

	for obstacle in obstacles:
		point_list.append(obstacle.getPoints())

	for points in point_list:
		for point in points:
			obstacle_points.append(point)
		for i in range(0,len(points)-1):
			j = i+1
			line_list.append((points[i],points[j]))
		line_list.append((points[-1],points[0]))

	for points in point_list:
		for i in range(len(points)):
			tmp_list = copy.copy(line_list)
			edge_successors = getEdges(points,i)
			corners = [(0,0),(1024,0),(1024,768),(0,768)]

			if (points[i],edge_successors[0]) in tmp_list:
				tmp_list.remove((points[i],edge_successors[0]))
			elif (edge_successors[0],points[i]):
				tmp_list.remove((edge_successors[0],points[i]))

			if (points[i],edge_successors[1]) in tmp_list:
				tmp_list.remove((points[i],edge_successors[1]))
			elif (edge_successors[1],points[i]):
				tmp_list.remove((edge_successors[1],points[i]))

			nearest_corner = findClosestUnobstructed(points[i],corners,tmp_list)

			if nearest_corner:
				pygame.draw.line(world.debug,(0,255,0),points[i],nearest_corner,1)
				# skip_first = False
				# skip_second = False
				# for j in range(len(points)-1):
				# 	if edge_successors[0] != points[j] and edge_successors[0] != points[j+1]:
				# 		if getIntersectPoint(points[j],points[j+1],nearest_corner,edge_successors[0]):
				# 			skip_first = True
				# 	if edge_successors[1] != points[j] and edge_successors[1] != points[j+1]:
				# 		if getIntersectPoint(points[j],points[j+1],nearest_corner,edge_successors[1]):
				# 			skip_second = True

				# if not skip_first:
				pygame.draw.line(world.debug,(0,255,0),nearest_corner,edge_successors[0],1)
				# if not skip_second:
				pygame.draw.line(world.debug,(0,255,0),nearest_corner,edge_successors[1],1)

	return nodes, edges, polys

	
