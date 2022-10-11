import numpy as np

simulation_time = 10
slot_duration = 10*10**(-6)
cw_base = 4
cw_max = 1024
ack = 2
sifs = 1
difs = 4
simulation_slots = 1000000
bandwidth = 8*10**(6)

def traffic_generator(arrival_rate):
	# Generate uniform distribution, Multipling size times two just to ensure enough samples to transmit
	uniform_distribution = np.random.uniform(low=0, high=1, size=arrival_rate * simulation_time * 2)
	# Convert to exponential distribution
	exponential_distribution = exponential_distribution = -(1 / arrival_rate) * np.log(1 - uniform_distribution)
	# Convert to interpacket slot times
	interpacket_time_slot = np.ceil(exponential_distribution / slot_duration)
	# Find the slot arrival time of a packet
	arrival_time_slot = np.cumsum(interpacket_time_slot)

	return arrival_time_slot

def transmit_packet(current_time_slot, backoff):
	current_time_slot = current_time_slot + difs + backoff + sifs + ack

def simulation(arrival_slot_1, arrival_slot_2):
	slot_index_1 = 0
	slot_index_2 = 0
	backoff_1 = 0
	backoff_2 = 0
	arrival_slot_1
	arrival_slot_2
	extendedBackoff = 0
	collisionCounter = 0

	# Initialize the startup timing slot
	current_time_slot = arrival_slot_1[0] if arrival_slot_1[0] <= arrival_slot_2[0] else arrival_slot_2[0]

	# Start simulation until simulation time exceeded
	while simulation_slots > current_time_slot:
		if backoff_1 == 0 or extendedBackoff != 0:
			backoff_1 = np.random.randint(0, cw_base*2**extendedBackoff)
		if backoff_2 == 0 or extendedBackoff != 0:
			backoff_2 = np.random.randint(0, cw_base*2**extendedBackoff)
		
		# Check if more than two frames are to compete for the same medium
		if arrival_slot_1[slot_index_1] <= current_time_slot and arrival_slot_2[slot_index_2] <= current_time_slot:
			# Check if for possible packet collision or detection of medium usage
			if backoff_1 == backoff_2:
				current_time_slot = current_time_slot + difs + backoff_1 + sifs + ack
				extendedBackoff += 1
				collisionCounter = collisionCounter + 1
			elif backoff_1 < backoff_2:
				transmit_packet(current_time_slot, backoff_1)
				slot_index_1 += 1
				# Reset transmission values
				backoff_1 = 0
				extendedBackoff = 0
				# Adjust backoff of competing frame
				backoff_2 = backoff_2 - backoff_1
			else:
				transmit_packet(current_time_slot, backoff_2)
				slot_index_2 += 1
				# Reset transmission values
				backoff_2 = 0
				extendedBackoff = 0
				# Adjust backoff of competing frame
				backoff_1 = backoff_1 - backoff_2
		elif arrival_slot_1[slot_index_1] <= current_time_slot:
			transmit_packet(current_time_slot, backoff_1)
			backoff_1 = 0
			slot_index_1 += 1
		elif arrival_slot_2[slot_index_2] <= current_time_slot:
			transmit_packet(current_time_slot, backoff_2)
			backoff_2 = 0
			slot_index_2 += 1
		# In idle, thus increment the time slot till something to transmit
		else:
			current_time_slot = current_time_slot + 1

	# Packet count that have been sent succesfully
	number_of_successes_1 = slot_index_1
	number_of_successes_2 = slot_index_2
	# Throughput
	throughput = number_of_successes_1 * (bandwidth / simulation_time)
	# Fairness Index
	fairness_index = number_of_successes_1 / number_of_successes_2

	return collisionCounter, throughput, fairness_index

def main():
	arrival_rates = [100, 200, 300, 400, 700, 1000]
	for arrival_rate in arrival_rates:
		arrival_slot_1 = traffic_generator(arrival_rate)
		arrival_slot_2 = traffic_generator(arrival_rate)
		collisions, throughput, fi = simulation(arrival_slot_1, arrival_slot_2)
		print("Collsions: {0}, Throughput: {1}, Fairness Index: {2}".format(collisions, throughput, fi))

main()