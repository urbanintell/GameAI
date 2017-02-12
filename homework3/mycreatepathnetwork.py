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


def myBuildPathNetwork(pathnodes,world,agent=None):
	lines = []
	
	obstacles = world.getObstacles()
	obstacle_points = []
	point_list = []
	line_list = []
	point_dict = {}
	maxRadius = agent.getMaxRadius()
	
	for obstacle in obstacles:
		point_list.append(obstacle.getPoints())

	for points in point_list:
		for point in points:
			obstacle_points.append(point)
		for i in range(0,len(points)-1):
			j = i+1
			line_list.append((points[i],points[j]))
		line_list.append((points[-1],points[0]))

	for node in pathnodes:
		tmp = copy.copy(pathnodes)
		tmp.remove(node)

		while tmp and findClosestUnobstructed(node,tmp,line_list):
			closest = findClosestUnobstructed(node,tmp,line_list)

			if point_dict.get(node,None):
				arr = point_dict[node]
				arr.append(closest)
				point_dict[node] = arr
			else:
				arr = []
				arr.append(closest)
				point_dict[node] = arr

			tmp.remove(closest)

	for source in pathnodes:
		if point_dict.get(source,None):
			target_list = point_dict[source]
			for target in target_list:
				skip = False
				for point in obstacle_points:
					if minimumDistance((source,target),point) < maxRadius:
						skip = True
				if not skip:
					lines.append((source,target))
			
			point_dict.pop(source, None)

	return lines


# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent=None):
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
			x = (triplet[0][0] + triplet[1][0])/2.0
			y = (triplet[0][1] + triplet[1][1])/2.0
			nodes.append((x,y))
			drawCross(world.debug,(x,y),(0,0,255),2,1)
		if not skip_arr[1]:
			pygame.draw.line(world.debug,(0,255,0),triplet[0],triplet[2],1)
			lines.append((triplet[0],triplet[2]))
			x = (triplet[0][0] + triplet[2][0])/2.0
			y = (triplet[0][1] + triplet[2][1])/2.0
			nodes.append((x,y))
			drawCross(world.debug,(x,y),(0,0,255),2,1)
		if not skip_arr[2]:
			pygame.draw.line(world.debug,(0,255,0),triplet[1],triplet[2],1)
			lines.append((triplet[1],triplet[2]))
			x = (triplet[1][0] + triplet[2][0])/2.0
			y = (triplet[1][1] + triplet[2][1])/2.0
			nodes.append((x,y))
			drawCross(world.debug,(x,y),(0,0,255),2,1)

		if (not skip_arr[0] and not skip_arr[1]) or (not skip_arr[0] and not skip_arr[2]) or (not skip_arr[1] and not skip_arr[2]):
			polys.append(triplet)
		elif not skip_arr[0] and not skip_arr[2]:
			polys.append(triplet)
		elif not skip_arr[0] and skip_arr[1] and skip_arr[2]:
			polys.append((triplet[0],triplet[1]))
		elif not skip_arr[1] and skip_arr[0] and skip_arr[2]:
			polys.append((triplet[0],triplet[2]))
		elif not skip_arr[2] and skip_arr[0] and skip_arr[1]:
			polys.append((triplet[1],triplet[2]))

	edges = myBuildPathNetwork(nodes,world,agent)

	return nodes,edges,polys

	
