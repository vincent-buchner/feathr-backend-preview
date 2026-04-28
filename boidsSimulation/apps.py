from django.apps import AppConfig
import threading
from seniorProjectBackendDjango.settings import SIMULATION_FPS

# class BoidssimulationConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'boidsSimulation'

class BoidssimulationConfig(AppConfig):
    name = 'boidsSimulation'

    def ready(self):
        from boidsSimulation.simulation.run import BoidsSimulation, SimulationRunner

        # Start the simulation in a new thread
        simulation = BoidsSimulation()
        simulation.setup()

        print("Starting simulation...")
        runner = SimulationRunner(simulation)
        sim_thread = threading.Thread(target=runner.run, daemon=True, kwargs={"fps": SIMULATION_FPS})
        sim_thread.start()
