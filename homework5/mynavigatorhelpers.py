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

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *

### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	obstacles = world.getLinesWithoutBorders()
	worldPoints = world.getPoints()

	# trimming path from source
	# reach the next accessible node in path from source 
	opt_start = 0
	for i in range(len(path)):
		if clearShotCopy(source,path[i],obstacles,worldPoints,agent):	# no obstacle or gate between destination and pathnode
			opt_start = i
	path = path[opt_start:]

	# trimming path from destination
	# reach destination from the last accessible node in path from destination
	opt_end = len(path)-1
	for i in range(len(path)-1,-1,-1):
		if clearShotCopy(dest,path[i],obstacles,worldPoints,agent):		# no obstacle or gate between destination and pathnode
			opt_end = i
	path = path[:opt_end+1]

	# trimming nodes between path
	# skipping all nodes which can be avoided if next available node is directly accessible
	index = 0
	while index<len(path):
		next_node = index+1

		for j in range(index+1,len(path),1):
			if clearShotCopy(path[index],path[j],obstacles,worldPoints,agent):	# no obstacle or gate between destination and pathnode
				next_node = j	
		if next_node != (index+1):
			path = path[:index+1]+path[next_node:]

		index+=1

	return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	agent = nav.agent
	current_pos = nav.agent.getLocation()

	# skip milliseconds, by approximating that target has been reached,
	# before it has been actually reached
	# if hasattr(agent, 'targets'):
	# 	for target in agent.targets:
	# 		if distance(current_pos, target) < agent.getMaxRadius()/3.0:
	# 			agent.targets.remove(target)

	# if the next destination is visible and walkable without any collison, 
	# move directly to that destination
	obstacles = nav.world.getLinesWithoutBorders()
	worldPoints = nav.world.getPoints()
	destination = nav.destination
	if destination is not None:
		if clearShotCopy(current_pos,destination,obstacles,worldPoints,agent):
			nav.setPath([])
			agent.moveToTarget(destination)
			return True

	# using the same logic from shortcutPath
	path = nav.getPath()
	next_node = -1
	if path:
		for i in range(len(path)):
			if clearShotCopy(current_pos,path[i],obstacles,worldPoints,agent):
				next_node = i

		if next_node != -1:
			nav.setPath(path[next_node:])
			agent.moveToTarget(path[next_node])
			return True

	return False


def clearShotCopy(p1, p2, worldLines, worldPoints, agent):
    
    if rayTraceWorld(p1,p2,worldLines) is None:     # no intersection
        for point in worldPoints:
            if minimumDistance((p1,p2),point) <= agent.getMaxRadius():
                return False    # plausible intersection
        return True
    else:   # intersection
        return False

