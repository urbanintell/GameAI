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
		self.states = [Idle, Move, AttackTower, AttackBase, AttackMinions]
		### Add your states to self.states (but don't remove Idle)


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
		self.agent.changeState(Idle,[Taunt])

		return None


##############################
### Move
###
### This is a state used for moving agents toward enemy sides.
### We exit out of this state once we are in attacking range of base or tower

class Move(State):

	def enter(self, oldstate):
		State.enter(self, oldstate)

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			towers = self.agent.world.getEnemyTowers(my_team)
			bases = self.agent.world.getEnemyBases(my_team)
			agent_pos = self.agent.position
			moving_to_tower = False

			for tower in towers:
				if tower.isAlive():			# redundant check
					self.agent.navigator.computePath(agent_pos, tower.position)
					moving_to_tower = True
					break

			if not moving_to_tower:			# Already moving to tower, skip checking for base
				for base in bases:
					if base.isAlive():		# redundant check
						self.agent.navigator.computePath(agent_pos, base.position)
						break

			if len(bases) == 0:
				self.agent.changeState(Idle,[AttackBase])


	def execute(self, delta = 0):
		State.execute(self, delta)
		
		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			towers = self.agent.world.getEnemyTowers(my_team)
			bases = self.agent.world.getEnemyBases(my_team)
			agent_pos = self.agent.position

			bullet_range = None
			if isinstance(self.agent.bulletclass,SmallBullet):
				bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
			else:
				bullet_range = SMALLBULLETRANGE

			moving_to_tower = False

			# move minions towards enemy, THIS IS SPARTAA
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
			else:
				stop_at_tower = False

				# check for the nearest tower and stop
				for tower in towers:
					if distance(agent_pos,tower.position) <= bullet_range:
						visible_towers = self.agent.getVisibleType(Tower)

						if len(towers) > 0:
							self.agent.stopMoving()
							self.agent.navigator.destination = tower.position
							self.agent.turnToFace(tower.position)
							self.agent.changeState(AttackTower,[Move])
							stop_at_tower = True
							break

				if not stop_at_tower:
					for base in bases:
						if base.isAlive() and len(towers) <= 0:
							if distance(agent_pos, base.position) <= bullet_range:
								visible_bases = self.agent.getVisibleType(Base)
								# TODO: if visible base position is same as nearest base, only then stop
								self.agent.stopMoving()
								self.agent.navigator.destination = base.position
								self.agent.turnToFace(base.position)
								self.agent.changeState(AttackBase,[Move])
								break

				visible_minions = self.agent.getVisibleType(Minion)
				enemy_npcs = self.agent.world.getEnemyNPCs(my_team)

				for minion in visible_minions:
					if minion in enemy_npcs and minion.isAlive():
						if distance(agent_pos,minion.position) <= bullet_range:
							self.agent.stopMoving()
							self.agent.turnToFace(minion.position)
							self.agent.shoot()
							self.agent.changeState(AttackMinions,[Move])
							break

				if len(bases) == 0:
					self.agent.changeState(Idle,[Move])

		return None


	def exit(self):
		State.exit(self)
		self.agent.stopMoving()


##############################
### Attack Tower
###
### This is a state used for shooting at enemy towers.
### We exit out of this state once we are done destroying the tower we are shooting at
### or we die in the process (BUT WE NEVER BACK DOWN).


class AttackTower(State):

	def enter(self, oldstate):
		State.enter(self, oldstate)

		self.agent.stopMoving()

		bullet_range = None
		if isinstance(self.agent.bulletclass,SmallBullet):
			bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
		else:
			bullet_range = SMALLBULLETRANGE

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			towers = self.agent.world.getEnemyTowers(my_team)
			agent_pos = self.agent.position

			for tower in towers:
				if tower.isAlive():		#redundant check, game engine ensures towers contain only alive towers
					if tower.position == self.agent.navigator.destination:
						self.agent.turnToFace(tower.position)
						self.agent.shoot()


	def execute(self, delta = 0):
		State.execute(self, delta)

		bullet_range = None
		if isinstance(self.agent.bulletclass,SmallBullet):
			bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
		else:
			bullet_range = SMALLBULLETRANGE

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			towers = self.agent.world.getEnemyTowers(my_team)
			agent_pos = self.agent.position

			didAttack = False
			for tower in towers:
				if tower.isAlive():		#redundant check, game engine ensures towers contain only alive towers
					if distance(agent_pos, tower.position) <= bullet_range and self.agent.navigator.destination and self.agent.navigator.destination == tower.position:
						self.agent.shoot()
						didAttack = True
						break

			if not didAttack:	# Tower being attacked previously died, change focus
				for tower in towers:
					if tower.isAlive():
						self.agent.changeState(Move,[AttackTower])
						break
						
			if len(towers) == 0:
				self.agent.changeState(Move,[AttackTower])

		return None


	def exit(self):
		State.exit(self)


##############################
### Attack Base
###
### This is a state used for shooting at enemy bases.
### We exit out of this state once we are done destroying the base we are shooting at
### or we die in the process (BUT WE NEVER BACK DOWN).


class AttackBase(State):

	def enter(self, oldstate):
		State.enter(self, oldstate)

		# print "Entered AttackBase State"
		self.agent.stopMoving()

		bullet_range = None
		if isinstance(self.agent.bulletclass,SmallBullet):
			bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
		else:
			bullet_range = SMALLBULLETRANGE

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			bases = self.agent.world.getEnemyBases(my_team)
			agent_pos = self.agent.position

			for base in bases:
				if base.isAlive():		# redundant check
					self.agent.turnToFace(base.position)
					self.agent.shoot()


	def execute(self, delta = 0):
		State.execute(self, delta)

		bullet_range = None
		if isinstance(self.agent.bulletclass,SmallBullet):
			bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
		else:
			bullet_range = SMALLBULLETRANGE

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			bases = self.agent.world.getEnemyBases(my_team)
			agent_pos = self.agent.position

			didAttack = False
			for base in bases:
				if base.isAlive():		# redundant check
					if distance(agent_pos, base.position) <= bullet_range:		# TODO: Multiple Base Logic
						self.agent.shoot()
						didAttack = True
						break

			if len(bases) == 0:
				# print "going to idle state"
				self.agent.changeState(Idle,[AttackBase])

		return None


	def exit(self):
		State.exit(self)


##############################
### Attack Minions
###
### This is a state used for shooting at enemy minions.
### We exit out of this state once there are no visible enemy minions in our range
### and go back to Move State


class AttackMinions(State):

	def enter(self, oldstate):
		State.enter(self, oldstate)

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			agent_pos = self.agent.position
			self.agent.stopMoving()

			bullet_range = None
			if isinstance(self.agent.bulletclass,SmallBullet):
				bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
			else:
				bullet_range = SMALLBULLETRANGE

			visible_minions = self.agent.getVisibleType(Minion)
			enemy_npcs = self.agent.world.getEnemyNPCs(my_team)

			for minion in visible_minions:
				if minion in enemy_npcs and minion.isAlive():
					if distance(agent_pos,minion.position) <= bullet_range:
						self.agent.stopMoving()
						self.agent.turnToFace(minion.position)
						self.agent.shoot()
						break


	def execute(self, delta = 0):
		State.execute(self, delta)

		bullet_range = None
		if isinstance(self.agent.bulletclass,SmallBullet):
			bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
		else:
			bullet_range = SMALLBULLETRANGE

		if self.agent.isAlive():
			my_team = self.agent.getTeam()
			agent_pos = self.agent.position

			bullet_range = None
			if isinstance(self.agent.bulletclass,SmallBullet):
				bullet_range = SMALLBULLETRANGE		# TODO: get bullet range automatically by class type checking
			else:
				bullet_range = SMALLBULLETRANGE

			visible_minions = self.agent.getVisibleType(Minion)
			enemy_npcs = self.agent.world.getEnemyNPCs(my_team)

			found_minion = False
			for minion in visible_minions:
				if minion in enemy_npcs and minion.isAlive():
					if distance(agent_pos,minion.position) <= bullet_range:
						self.agent.turnToFace(minion.position)
						self.agent.shoot()
						found_minion = True
						break

			if not found_minion:
				self.agent.changeState(Move,[AttackMinions])

		return None


	def exit(self):
		State.exit(self)
