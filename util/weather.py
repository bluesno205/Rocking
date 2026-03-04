import carla

class Weather:
    def __init__(self, world):
        self.world = world
        self.weather_id = None  # Initialize weather_id

    def set_weather(self, weather_id):
        """
        Set the weather in CARLA using the given weather ID.

        :param weather_id: An integer representing the desired weather preset.
        """
        weather_presets = {
            0: ("Default", carla.WeatherParameters.ClearNoon),
            1: ("ClearNoon", carla.WeatherParameters.ClearNoon),
            2: ("CloudyNoon", carla.WeatherParameters.CloudyNoon),
            3: ("WetNoon", carla.WeatherParameters.WetNoon),
            4: ("WetCloudyNoon", carla.WeatherParameters.WetCloudyNoon),
            5: ("MidRainyNoon", carla.WeatherParameters.MidRainyNoon),
            6: ("HardRainNoon", carla.WeatherParameters.HardRainNoon),
            7: ("SoftRainNoon", carla.WeatherParameters.SoftRainNoon),
            8: ("ClearSunset", carla.WeatherParameters.ClearSunset),
            9: ("CloudySunset", carla.WeatherParameters.CloudySunset),
            10: ("WetSunset", carla.WeatherParameters.WetSunset),
            11: ("WetCloudySunset", carla.WeatherParameters.WetCloudySunset),
            12: ("MidRainSunset", carla.WeatherParameters.MidRainSunset),
            13: ("HardRainSunset", carla.WeatherParameters.HardRainSunset),
            14: ("SoftRainSunset", carla.WeatherParameters.SoftRainSunset),
        }

        if weather_id in weather_presets:
            weather_name, weather_params = weather_presets[weather_id]
            self.world.set_weather(weather_params)
            self.weather_id = weather_id  # Set the current weather ID
            print(f"Weather : {weather_id} - {weather_name}")
        else:
            print(f"Invalid weather ID: {weather_id}. Please choose a value between 0 and 14.")

def update_weather_params(weather_params, case):
    """
    Update weather parameters based on the case.

    :param weather_params: Weather object containing parameters
    :param case: A list or tuple where case[0] is the weather ID
    """
    weather_id = case[0]
    weather_params.set_weather(weather_id)

def modify_weather(world, weather_params):
    """
    Modify the weather in the specified world using the given parameters.

    :param world: The CARLA world object
    :param weather_params: Weather object containing parameters
    """
    try:
        weather_params.set_weather(weather_params.weather_id)  # Use the stored weather_id
    except Exception as e:
        print(f"Error modifying weather: {e}")

