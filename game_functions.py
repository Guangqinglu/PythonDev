# -!- coding: utf-8 -!-
import sys
from time import sleep
import pygame
from bullet import Bullet
from alien import Alien
			
def check_keydown_events(event, ai_settings, screen, ship, bullets):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True
	elif event.key == pygame.K_SPACE:
		#发射子弹
		fire_bullet(ai_settings, screen, ship, bullets)
	elif event.key == pygame.K_q:
		sys.exit()

def check_keyup_events(event, ship):
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	if event.key == pygame.K_LEFT:
		ship.moving_left = False

def check_events(ai_settings, screen, stats, play_button, ship, aliens, bullets):
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, play_button, ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, play_button, ship, aliens, bullets, mouse_x, mouse_y):
	#在玩家单击play按钮开始新游戏
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:
		#隐藏光标
		pygame.mouse.set_visible(False)
		#重置游戏统计信息
		stats.reset_stats()
		stats.game_active = True
		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()
		#创建一群新的外星人，并让飞船居中
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
	
	screen.fill(ai_settings.bg_color)
	#遍历子弹，重绘子弹
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	
	ship.blitme()
	aliens.draw(screen)
	#显示得分
	sb.show_score()
	#如果游戏处于非活动状态，就绘制play按钮
	if not stats.game_active:
		play_button.draw_button()
	pygame.display.flip()
	
def fire_bullet(ai_settings, screen, ship, bullets):
	#限制子弹数量
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
	bullets.update()
	#删除已消失的子弹
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	#检查是否子弹击中了外星人
		check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	if collisions:
		stats.score += ai_settings.alien_points
		sb.prep_score()
	if len(aliens) == 0:
		# 删除现有的子弹并新建一群外星人
		bullets.empty()
		create_fleet(ai_settings, screen, ship, aliens)

def get_number_aliens_x(ai_settings, alien_width):
	#计算每行可容纳多少个外星人
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
	available_space_y = ai_settings.screen_height - 3 * alien_height - ship_height
	number_rows = int(available_space_y / (2 * alien_height))
	return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	#创建一个外星人并将其放在当前行
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
	#创建外星人群
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

	#创建第一行外星人
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			#创建一个外星人并加入当前行
			create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
	#有外星人到达边缘是采取相应的措施
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break

def change_fleet_direction(ai_settings, aliens):
	#将整群外星人下移，并改变方向
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
	#响应被外星人撞到的飞船，将ship_left减1
	if stats.ship_left > 0:
		stats.ship_left -= 1
		#清空外星人列表和子弹列表
		aliens.empty()
		bullets.empty()
		#创建一群新的外星人，并将飞船放到屏幕底端中央
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
		#暂停
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
	#检查是否有外星人处于屏幕边缘，并更新外星人的位置
	check_fleet_edges(ai_settings, aliens)
	aliens.update()
	#检测外星人和飞船之间的碰撞
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
	check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets)

def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets):
	#检查是否有外星人到达屏幕底端
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			#像飞船被撞到一样进行处理
			ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
			break