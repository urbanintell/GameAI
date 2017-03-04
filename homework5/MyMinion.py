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
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle, Move]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###

		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)


############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		self.agent.changeState(Move,[Idle])

		return None


class Move(State):

	def enter(self, oldstate):
		State.enter(self, oldstate)
		my_team = self.agent.getTeam()
		towers = self.agent.world.getEnemyTowers(my_team)
		bases = self.agent.world.getEnemyBases(my_team)
		agent_pos = self.agent.position
		moving_to_tower = False

		for tower in towers:
			if tower.isAlive():
				self.agent.navigator.computePath(agent_pos, tower.position)
				moving_to_tower = True
				break

		if not moving_to_tower:
			for base in bases:
				if base.isAlive():
					self.agent.navigator.computePath(agent_pos, base.position)
					break


	def execute(self, delta = 0):
		State.execute(self, delta)
		
		my_team = self.agent.getTeam()
		towers = self.agent.world.getEnemyTowers(my_team)
		bases = self.agent.world.getEnemyBases(my_team)
		agent_pos = self.agent.position

		moving_to_tower = False

		if not self.agent.isMoving():
			for tower in towers:
				if tower.isAlive():
					self.agent.navigator.computePath(agent_pos, tower.position)
					moving_to_tower = True
					break

			if not moving_to_tower:
				for base in bases:
					if base.isAlive():
						self.agent.navigator.computePath(agent_pos, base.position)
						break

		return None
##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

