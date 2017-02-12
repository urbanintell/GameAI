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

# Creates the pathnetwork as a list of lines between all pathnodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
	lines = []
	
	obstacles = world.getObstacles()
	point_list = []
	line_list = []
	point_dict = {}
	
	for obstacle in obstacles:
		point_list.append(obstacle.getPoints())

	for points in point_list:
		for i in range(0,len(points)):
			for j in range(i+1,len(points)):
				line_list.append((points[i],points[j]))

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
				lines.append((source,target))
			
			point_dict.pop(source, None)
			
	return lines
