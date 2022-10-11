import numpy as np

class Simulation:
    # Simulation Parameters
    arrival_rates = [100, 200, 300, 400, 700, 1000]
    simulation_time = 10
    slot_duration = 10*10**(-6)
    simulation_slots = simulation_time / slot_duration
    bandwidth = 8*10**(6) # In bits per second

    # Backoff Paremeters
    cw_base = 4
    cw_max = 1024

    # Packet Parameters
    ack = 2
    sifs = 1
    difs = 4

    # Tracking Variables
    extendedBackoff = 0
    collisionCounter = 0
    current_time_slot = 0

    def transmit_packet(self, backoff):
        self.current_time_slot = self.current_time_slot + self.difs + backoff + self.sifs + self.ack

    def run_simulation(self):
        simulation_results = []
        for rate in self.arrival_rates:
            performance_metrics = self.start_simulation(rate)
            simulation_results.append(performance_metrics)
        return simulation_results
    
    def start_simulation(self, rate):
        # Create transmitting routers
        router1 = Router(rate)
        router2 = Router(rate)

        # Initialize the startup timing slot
        self.current_time_slot = router1.arrival_slot[0] if router1.arrival_slot[0] <= router2.arrival_slot[0] else router2.arrival_slot[0]

        # Start simulation until simulation time exceeded
        while self.simulation_slots > self.current_time_slot:
            if router1.backoff == 0 or self.extendedBackoff != 0:
                router1.backoff = np.random.randint(0, self.cw_base*2**self.extendedBackoff)
            if router2.backoff == 0 or self.extendedBackoff != 0:
                router2.backoff = np.random.randint(0, self.cw_base*2**self.extendedBackoff)
            
            # Check if more than two frames are to compete for the same medium
            if router1.arrival_slot[router1.slot_index] <= self.current_time_slot and router2.arrival_slot[router2.slot_index] <= self.current_time_slot:
                # Check if for possible packet collision or detection of medium usage
                if router1.backoff == router2.backoff:
                    self.current_time_slot = self.current_time_slot + self.difs + router1.backoff + self.sifs + self.ack
                    self.extendedBackoff += 1
                    self.collisionCounter += 1
                elif router1.backoff < router2.backoff:
                    self.transmit_packet(router1.backoff)
                    router1.slot_index += 1
                    # Reset transmission values
                    router1.backoff = 0
                    self.extendedBackoff = 0
                    # Adjust backoff of competing frame
                    router2.backoff = router2.backoff - router1.backoff
                else:
                    self.transmit_packet(router2.backoff)
                    router2.slot_index += 1
                    # Reset transmission values
                    router2.backoff = 0
                    self.extendedBackoff = 0
                    # Adjust backoff of competing frame
                    router1.backoff = router1.backoff - router2.backoff
            elif router1.arrival_slot[router1.slot_index] <= self.current_time_slot:
                self.transmit_packet(router1.backoff)
                router1.backoff = 0
                router1.slot_index += 1
            elif router2.arrival_slot[router2.slot_index] <= self.current_time_slot:
                self.transmit_packet(router2.backoff)
                router2.backoff = 0
                router2.slot_index += 1
            # In idle, thus increment the time slot till something to transmit
            else:
                self.current_time_slot = self.current_time_slot + 1

        # Packet count that have been sent succesfully
        number_of_successes_1 = router1.slot_index
        number_of_successes_2 = router2.slot_index

        throughput = number_of_successes_1 * (self.bandwidth / self.simulation_time)
        fairness_index = number_of_successes_1 / number_of_successes_2

        print(f"Collisions: {self.collisionCounter}, Throughput: {throughput * 10**(-6):.{2}f}, fairness_index: {fairness_index:.{2}f}")

        performance_metrics = {'collisions': self.collisionCounter, 'throughput': throughput, 'fairness index:': fairness_index}
        return performance_metrics

class Router(Simulation):
    def __init__(self, rate):
       self.arrival_slot = self.generator_traffic(rate)
       self.slot_index = 0
       self.backoff = 0

    def generator_traffic(self, arrival_rate):
        # Generate uniform distribution. Multipling size times two just to ensure enough samples to transmit
        uniform_distribution = np.random.uniform(low=0, high=1, size=arrival_rate * self.simulation_time * 2)
        # Convert uniform distribution to exponential distribution
        exponential_distribution = exponential_distribution = -(1 / arrival_rate) * np.log(1 - uniform_distribution)
        # Transform the packet transmittion time to interpacket slot times
        interpacket_time_slot = np.ceil(exponential_distribution / self.slot_duration)
        # Find the approximated packet slot arrival time
        arrival_time_slot = np.cumsum(interpacket_time_slot)
        
        return arrival_time_slot

def main():
    simulation = Simulation()
    results = simulation.run_simulation()
    
main()