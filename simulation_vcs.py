import numpy as np

class Simulation:
    # Simulation Parameters
    arrival_rates = [100, 200, 300, 400, 700, 1000]
    simulation_time = 10
    slot_duration = 10 * 10**(-6)
    simulation_slots = round(simulation_time / slot_duration)
    bandwidth = 8 * 10**(6) # In bits per second
    packet_size = 1000 * 8 # In bits

    # Backoff Paremeters
    cw_base = 4
    cw_max = 1024

    # Packet Parameters
    difs = 4
    sifs = 1
    rts = 2
    cts = 2
    ack = 2
    tx_slots = packet_size / (bandwidth * slot_duration)

    def generate_backoff(self, extension):
        return np.random.randint(0, self.cw_base * 2**extension)

    def generate_transmission(self, backoff):
        return self.difs + backoff + self.rts + self.sifs + self.cts + self.sifs + self.tx_slots + self.sifs + self.ack

    def run_simulation(self):
        simulation_report = []
        for rate in self.arrival_rates:
            performance_metrics = self.start_simulation(rate)
            simulation_report.append(performance_metrics)
        return simulation_report
    
    def start_simulation(self, rate):
        # Create transmitting routers
        router1 = Router(rate)
        router2 = Router(rate)

        # Tracking Variables
        extend_backoff = 0
        collision_counter = 0

        # Initialize the startup timing slot
        current_time_slot = router1.arrival_slot[0] if router1.arrival_slot[0] <= router2.arrival_slot[0] else router2.arrival_slot[0]

        # Start simulation until simulation time exceeded
        while self.simulation_slots > current_time_slot:
            if router1.backoff < 0 or extend_backoff != 0:
                router1.backoff = self.generate_backoff(extend_backoff)
            if router2.backoff < 0 or extend_backoff != 0:
                router2.backoff = self.generate_backoff(extend_backoff)
            
            # Check if more than two frames are to compete for the same medium
            if router1.arrival_slot[router1.slot_index] <= current_time_slot and router2.arrival_slot[router2.slot_index] <= current_time_slot:
                # Check if for possible packet collision or detection of medium usage
                if router1.backoff == router2.backoff:
                    current_time_slot += self.difs + router1.backoff + self.rts + self.sifs + self.cts
                    extend_backoff += 1
                    collision_counter += 1
                elif router1.backoff < router2.backoff:
                    current_time_slot += self.generate_transmission(router1.backoff)
                    router1.slot_index += 1
                    # Adjust backoff of competing frame
                    router2.backoff = router2.backoff - router1.backoff
                    # Reset transmission values
                    router1.backoff = -1
                    extend_backoff = 0
                else:
                    current_time_slot += self.generate_transmission(router2.backoff)
                    router2.slot_index += 1
                    # Adjust backoff of competing frame
                    router1.backoff = router1.backoff - router2.backoff
                    # Reset transmission values
                    router2.backoff = -1
                    extend_backoff = 0
            elif router1.arrival_slot[router1.slot_index] <= current_time_slot:
                current_time_slot += self.generate_transmission(router1.backoff)
                router1.backoff = -1
                router1.slot_index += 1
            elif router2.arrival_slot[router2.slot_index] <= current_time_slot:
                current_time_slot += self.generate_transmission(router2.backoff)
                router2.backoff = -1
                router2.slot_index += 1
            # In idle, thus increment the time slot till something to transmit
            else:
                current_time_slot += 1

        # Packet count that have been sent succesfully
        number_of_successes_1 = router1.slot_index
        number_of_successes_2 = router2.slot_index

        # Clean up post simulation to improve performance
        del router1, router2

        # Thorughput for each respective router
        throughput_1 = number_of_successes_1 * (self.packet_size / self.simulation_time)
        throughput_2 = number_of_successes_2 * (self.packet_size / self.simulation_time)

        fairness_index = number_of_successes_1 / number_of_successes_2

        print(f"------------------------Simulation with an arrival rate of {rate} frames/sec------------------------")
        print(f"Router 1 - Total packets succesfully sent: {number_of_successes_1}, Router 2 - Total packets succesfully sent: {number_of_successes_2}")
        print(f"Collisions: {collision_counter}, Router 1 Throughput: {throughput_1 * 10**(-3):.{2}f} Kbps, Router 2 Throughput: {throughput_2 * 10**(-3):.{2}f} Kbps, FI: {fairness_index:.{2}f}")

        performance_metrics = {'collisions': collision_counter, 'throughput_r1': throughput_1, 'throughput_r2': throughput_2, 'fairness index:': fairness_index}
        
        return performance_metrics

class Router(Simulation):
    def __init__(self, rate):
       self.arrival_slot = self.generate_traffic(rate)
       self.slot_index = 0
       self.backoff = -1

    def generate_traffic(self, arrival_rate):
        # Generate uniform distribution
        uniform_distribution = np.random.uniform(low=0, high=1, size=arrival_rate * self.simulation_time)
        # Convert uniform distribution to exponential distribution
        exponential_distribution = -(1 / arrival_rate) * np.log(1 - uniform_distribution)
        # Transform the packet transmittion time to interpacket slot times
        interpacket_time_slot = np.ceil(exponential_distribution / self.slot_duration)
        # Find the approximated packet slot arrival time
        arrival_time_slot = np.cumsum(interpacket_time_slot)

        # Pad with extra values arriaval times that are greater then simulation tim so there is no overflow when reading data
        arrival_time_slot_padded = np.append(arrival_time_slot, np.full(arrival_rate * self.simulation_time, self.simulation_slots))
        
        return arrival_time_slot_padded

def main():
    simulation = Simulation()
    simulation_report = simulation.run_simulation()

main()