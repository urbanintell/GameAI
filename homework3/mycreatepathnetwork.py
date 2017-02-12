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
	
	dim = world.getDimensions()
	obstacles = world.getObstacles()
	obstacle_points = []
	point_list = []
	line_list = []
	new_lines = []
	point_dict = {}
	maxRadius = agent.getMaxRadius()
	world_points = world.points
	corners = [(0,0),(dim[0],0),dim,(0,dim[1])]
	triplets = []
	lines = world.lines
	
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
		for i in range(len(points)-1):
			for j in range(i+1,len(points)):
				lines.append((points[i],points[j]))

	for i in range(len(world_points)-2):
		for j in range(i+1,len(world_points)-1):
			for k in range(j+1,len(world_points)):
				skip = False
				for points in point_list:
					if world_points[i] in points and world_points[j] in points and world_points[k] in points:
						skip = True
						break
				if not skip:
					triplet = ((world_points[i],world_points[j],world_points[k]))
					triplets.append(triplet)

	for triplet in triplets:
		skip_arr = [False] * 3
		for i in range(len(triplet)-1):
			for j in range(i+1,len(triplet)):
				if rayTraceWorldNoEndPoints(triplet[i],triplet[j],lines):
					if i == 0 and j == 1:
						skip_arr[0] = True
					elif i == 0 and j == 2:
						skip_arr[1] = True
					elif i == 1 and j == 2:
						skip_arr[2] = True

		if not skip_arr[0]:
			pygame.draw.line(world.debug,(0,255,0),triplet[0],triplet[1],1)
			lines.append((triplet[0],triplet[1]))
		if not skip_arr[1]:
			pygame.draw.line(world.debug,(0,255,0),triplet[0],triplet[2],1)
			lines.append((triplet[0],triplet[2]))
		if not skip_arr[2]:
			pygame.draw.line(world.debug,(0,255,0),triplet[1],triplet[2],1)
			lines.append((triplet[1],triplet[2]))


	# for points in point_list:
	# 	for i in range(len(points)):
	# 		tmp_list = copy.copy(line_list)
	# 		edge_successors = getEdges(points,i)
	# 		corners = [(0,0),(dim[0],0),dim,(0,dim[1])]

	# 		if (points[i],edge_successors[0]) in tmp_list:
	# 			tmp_list.remove((points[i],edge_successors[0]))
	# 		elif (edge_successors[0],points[i]):
	# 			tmp_list.remove((edge_successors[0],points[i]))

	# 		if (points[i],edge_successors[1]) in tmp_list:
	# 			tmp_list.remove((points[i],edge_successors[1]))
	# 		elif (edge_successors[1],points[i]):
	# 			tmp_list.remove((edge_successors[1],points[i]))

	# 		nearest_corner = findClosestUnobstructed(points[i],corners,tmp_list)

	# 		if nearest_corner:
	# 			if len(new_lines) > 0:
	# 				# skip = False
	# 				# for line in new_lines:
	# 				# 	if calculateIntersectPoint(line[0],line[1],nearest_corner,points[i]):
	# 				# 		pt = calculateIntersectPoint(line[0],line[1],nearest_corner,points[i])
	# 				# 		if pt not in corners:
	# 				# 			skip = True
	# 				# 			break
	# 				# if not skip:
	# 				# Try to Build Polygons (triangles)

	# 				pygame.draw.line(world.debug,(0,255,0),points[i],nearest_corner,1)
	# 				new_lines.append((points[i],nearest_corner))
	# 			else:
	# 				pygame.draw.line(world.debug,(0,255,0),points[i],nearest_corner,1)
	# 				new_lines.append((points[i],nearest_corner))

	# 			skip_first = False
	# 			skip_second = False
	# 			first_count = 0
	# 			second_count = 0
	# 			for j in range(len(points)-1):
	# 				if calculateIntersectPoint(points[j],points[j+1],nearest_corner,edge_successors[0]):
	# 					first_count += 1
	# 				if calculateIntersectPoint(points[j],points[j+1],nearest_corner,edge_successors[1]):
	# 					second_count += 1

	# 			if calculateIntersectPoint(points[-1],points[0],nearest_corner,edge_successors[0]):
	# 				first_count += 1
	# 			if calculateIntersectPoint(points[-1],points[0],nearest_corner,edge_successors[1]):
	# 				second_count += 1

	# 			if first_count == 2:
	# 				for line in new_lines:
	# 					if calculateIntersectPoint(line[0],line[1],nearest_corner,edge_successors[0]):
	# 						pt = calculateIntersectPoint(line[0],line[1],nearest_corner,edge_successors[0])
	# 						if pt not in corners:	
	# 							skip_first = True
	# 							break
	# 				if not skip_first:
	# 					pygame.draw.line(world.debug,(0,255,0),nearest_corner,edge_successors[0],1)
	# 					new_lines.append((nearest_corner,edge_successors[0]))
	# 			if second_count == 2:
	# 				for line in new_lines:
	# 					if calculateIntersectPoint(line[0],line[1],nearest_corner,edge_successors[1]):
	# 						pt = calculateIntersectPoint(line[0],line[1],nearest_corner,edge_successors[1])
	# 						if pt not in corners:
	# 							skip_second = True
	# 							break
	# 				if not skip_second:
	# 					pygame.draw.line(world.debug,(0,255,0),nearest_corner,edge_successors[1],1)
	# 					new_lines.append((nearest_corner,edge_successors[1]))


	return nodes, edges, polys

	
