import json
import requests
import psycopg2
from datetime import datetime
from sys import argv
import ConfigParser

lane = argv[1]
options = ['top', 'jungle', 'middle', 'adc', 'support']
if lane not in options:
	print "Valid options are 'top', 'jungle', 'middle', 'adc', and 'support'"
	print "You input: " + lane
	exit()
print "Updating table for " + lane + " lane."

config = ConfigParser.ConfigParser()
config.read("/etc/postgresql/.config")
pwd = config.get("configuration", "password")


#limit max is 50
#as of 9-8-16
#res = requests.get('http://api.champion.gg/stats/role/Top/mostWinning?api_key=b4b7513eb8b46d900cad595eb20327c3&page=1&limit=50')
#res2 = requests.get('http://api.champion.gg/stats/role/Top/mostWinning?api_key=b4b7513eb8b46d900cad595eb20327c3&page=2&limit=50')

res = requests.get('http://api.champion.gg/stats/role/' + lane + '/mostWinning?api_key=b4b7513eb8b46d900cad595eb20327c3&page=1&limit=50')
res2 = requests.get('http://api.champion.gg/stats/role/' + lane + '/mostWinning?api_key=b4b7513eb8b46d900cad595eb20327c3&page=2&limit=50')

try:
	conn = psycopg2.connect("dbname='ranking_snapshots' user='tyler' host='localhost' password='" + pwd + "'")	
	cursor = conn.cursor()
except:
	print "Unable to connect to ranking_snapshots"
	exit()


feed = 'data'
data = res.json()[feed]
data2 = res2.json()[feed]
list1_length = len(data)
list2_length = len(data2)
#print list1_length
#print list2_length
pages = [data, data2]

general_list_json = ['winPercent',
		'playPercent',
		'banRate',
		'experience',
		'kills',
		'deaths',
		'assists',
		'largestKillingSpree',
		'totalDamageDealtToChampions',
		'totalDamageTaken',
		'totalHeal',
		'minionsKilled',
		'neutralMinionsKilledEnemyJungle',
		'neutralMinionsKilledTeamJungle',
		'goldEarned',
		'overallPosition',
		'overallPositionChange']

general_list_postgres = ['win_rate',
			'play_rate',
			'ban_rate',
			'player_avg_games',
			'kills',
			'deaths',
			'assists',
			'killing_spree',
			'damage_dealt',
			'damage_taken',
			'total_healing',
			'minions_killed',
			'enemy_jungle_cs',
			'ally_jungle_cs',
			'gold_earned',
			'role_position',
			'position_change']


#for i in range(0, 1):
for data in pages:
#for i in range(0, list1_length):
	for i in range(0, len(data)):
		key_value = []
		data_general = data[i]['general']

		rank = (i+1) 
		key_value.append(('rank', rank))

		champion = data[i]['name']
		key_value.append(('champion', "'" + champion + "'"))
		#win_rate = data_general['winPercent'] 
		#play_rate = data_general

		for j in range(0, len(general_list_json)):
			append_me = (general_list_postgres[j], data_general[general_list_json[j]])
			key_value.append(append_me)

		SQL = "INSERT INTO " + lane + "_rankings (rank, champion, win_rate, play_rate, ban_rate, player_avg_games" + \
			", kills, deaths, assists, killing_spree, damage_dealt, damage_taken, total_healing" + \
			", minions_killed, enemy_jungle_cs, ally_jungle_cs, gold_earned, role_position, position_change" + \
			", snapshot_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
		data_string = ""	
		for left, right in key_value:
			if data_string != "":
				data_string += ", "
			data_string += str(right)
	
		#data_string = (str(data_string + ", TIMESTAMP '" + datetime.now().isoformat() + "'"), )
		data_string = (key_value[0][1],
				key_value[1][1],
				key_value[2][1],
				key_value[3][1],
				key_value[4][1],
	                        key_value[5][1],
	                        key_value[6][1],
	                        key_value[7][1],
	                        key_value[8][1],
	                        key_value[9][1],
	                        key_value[10][1],
	                        key_value[11][1],
	                        key_value[12][1],
	                        key_value[13][1],
	                        key_value[14][1],
	                        key_value[15][1],
	                        key_value[16][1],
	                        key_value[17][1],
	                        key_value[18][1],
				datetime.now().isoformat())
		#print SQL
		#print data_string
		cursor.execute(SQL, data_string)
		conn.commit()
