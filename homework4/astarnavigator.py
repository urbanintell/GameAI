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
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
			
class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)
		
	### Create the pathnode network and pre-compute all shortest paths along the network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		### Make sure the next and dist matricies exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the pathnodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					# print len(self.pathnetwork)
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					# print len(newnetwork)
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork


def astar(init, goal, network):

	# source of AStar algorithm is taken from WikiPedia
	# https://en.wikipedia.org/wiki/A*_search_algorithm

	path = []
	
	# The set of nodes already evaluated
	closed = []

	# The set of currently discovered nodes that are not evaluated yet.
 	# Initially, only the start node is known.
 	open_arr = []
 	open_arr.append(init)

	# For each node, which node it can most efficiently be reached from.
 	# If a node can be reached from many nodes, cameFrom will eventually contain the
 	# most efficient previous step.
    came_from = {}

    # For each node, the cost of getting from the start node to that node.
    # default value is infinity
	g_score = {}
    for edge in network:
    	for node in edge:
    		if node not in g_score:
    			g_score[node] = float("inf")

    # The cost of going from start to start is zero.
    g_score[init] = 0

    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. That value is partly known, partly heuristic.
    # Default value is infinity
    f_score = {}
    for edge in network:
    	for node in edge:
    		if node not in f_score:
    			f_score[node] = float("inf")

    # For the first node, that value is completely heuristic.
    f_score[init] = distance(init,goal)

    current = init

    while len(open_arr) > 0:
    	# node in open list having the lowest fScore value
    	current = min(f_score,key=f_score.get)
    	if correct == goal:
    		path = buildPath(came_from,current)
    		break

    	open_arr.remove(current)
    	f_score.pop(current, None)	# this line ensures that 'current = min(fScore,key=fScore.get)' does it job correctly
    	closed.append(current)

    	for edge in network:
    		if current in edge:
    			tup_list = list(edge)
    			tup_list.remove(current)
    			neighbor = tup_list[0]

    			if neighbor in closed:	# ignore the neighbor which has already been evaluated
    				continue

    			# The distance from start to a neighbor
    			tentative_g_score = g_score[current] + distance(current,neighbor)
    			if neighbor not in open_arr:	# Discover a new node
    				open_arr.append(neighbor)
    			elif tentative_g_score >= g_score[neighbor]:	# This is not a better path
    				continue

    			# This path is the best until now. Record it!
    			came_from[neighbor] = current
    			g_score[neighbor] = tentative_g_score
    			f_score[neighbor] = g_score[neighbor] + distance(neighbor,goal)

	return path, closed
	

def buildPath(came_from, current):
	path = [current]
	while current in came_from:
		current = came_from[current]
		path.insert(0,current)
	return path


def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###

	### YOUR CODE GOES ABOVE HERE ###
	return None


def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###

	### YOUR CODE GOES ABOVE HERE ###
	return None


### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return False

